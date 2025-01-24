import os
from pydantic import BaseModel
from typing import Any
import requests


from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch

import config


DIR = os.path.dirname(os.path.realpath(__file__))


OPENSEARCH_PASSWORD = "<YOUR_PASSWORD>"  # See script/.env

URL = "<IP_of_this_container>"
PORT = "<PORT_of_this_container>"

EMB = "dragonkue/BGE-m3-ko"
EMB_PATH = os.path.join(DIR, "models", EMB)

# 모델 디렉토리가 존재하는지 확인
if os.path.exists(EMB_PATH):
    print(f"모델이 이미 로컬에 존재합니다: {EMB_PATH}")
    emb = SentenceTransformer(EMB_PATH)  # 로컬에서 모델 로드
else:
    print(f"모델이 로컬에 없습니다. 다운로드 중: {EMB}")
    emb = SentenceTransformer(EMB)  # Hugging Face에서 모델 다운로드
    emb.save(EMB_PATH)  # 모델을 지정된 경로에 저장
    print(f"모델이 저장되었습니다: {EMB_PATH}")

emb.cuda(0)

opensearch = OpenSearch(
    hosts=[{"host": URL, "port": PORT}],
    http_auth=("admin", OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)

app = FastAPI()


class Name(BaseModel):
    name: str


class Chunk(BaseModel):
    index_name: str
    key: Any = None
    content: str = None
    category1: str = None
    category2: str = None
    category3: str = None
    page: int = None
    chunk_id: int = None
    url: str = None


############# 인덱스 관련 #################


@app.post("/app/create_index/")
def create_index(chunk: Chunk):
    content_mapping = {
        "settings": {
            "index": {
                "replication": {"type": "DOCUMENT"},
                "refresh_interval": "5s",
                "number_of_shards": "1",
                "knn.algo_param": {"ef_search": "100"},
                "knn": "true",
                "analysis": {
                    "analyzer": {
                        "ngram_analyzer": {
                            "filter": ["lowercase"],
                            "type": "custom",
                            "tokenizer": "ngram_tokenizer",
                        }
                    },
                    "tokenizer": {
                        "ngram_tokenizer": {
                            "token_chars": ["letter", "digit"],
                            "min_gram": "2",
                            "type": "ngram",
                            "max_gram": "3",
                        }
                    },
                },
            }
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "content": {
                    "type": "text",
                    "analyzer": "ngram_analyzer",
                    "search_analyzer": "ngram_analyzer",
                },
                "content_morph": {
                    "type": "text",
                    "analyzer": "ngram_analyzer",
                    "search_analyzer": "ngram_analyzer",
                },
                "content_vector": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "engine": "nmslib",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {"ef_construction": 200, "m": 16},
                    },
                },
            }
        },
    }

    try:
        opensearch.indices.create(index=chunk.index_name, body=content_mapping)
        return {"status_code": 200, "status": "success", "message": "인덱스 생성 성공"}
    except Exception as e:
        return {"status_code": 500, "status": "fail", "message": f"Error: {str(e)}"}


@app.post("/app/delete_index/")
def delete_index(chunk: Chunk):
    try:
        opensearch.indices.delete(index=chunk.index_name)
        return {"status_code": 200, "status": "success", "message": "인덱스 삭제 성공"}
    except Exception as e:
        return {"status_code": 500, "status": "fail", "message": f"Error: {str(e)}"}


############# 청크 관련 #################


@app.post("/app/index_chunk/")
def index_chunk(chunk: Chunk):
    embedding = emb.encode(chunk.content)
    embedding = embedding.tolist()

    morph_data = {"text": chunk.content}
    morph_url = f"http://{config.morph_url}:{config.morph_port}/app/morph"
    morph_response = requests.post(url=morph_url, json=morph_data)
    if morph_response.status_code == 200:
        morph_response = morph_response.json()
        word = morph_response["text"]
    else:
        word = ""

    data = {
        "content": chunk.content,
        "content_morph": word,
        "content_vector": embedding,
        "category1": chunk.category1,
        "category2": chunk.category2,
        "category3": chunk.category3,
        "page": chunk.page,
        "chunk_id": chunk.chunk_id,
        "key": chunk.key,
        "url": chunk.url,
    }

    response = opensearch.index(index=chunk.index_name, body=data, id=chunk.key)

    return {"status_code": 200, "status": "success", "message": "청크 색인 성공"}


@app.post("/app/delete_chunk/")
def delete_chunk(chunk: Chunk):
    response = opensearch.delete(index=chunk.index_name, id=chunk.key)
    return {"status_code": 200, "status": "success", "message": "청크 삭제 성공"}


############# 검색 관련 #################
# TODO: 구현할거


@app.post("/app/ensemble_search/")
def ensemble_search(chunk: Chunk):
    data = {}

    response = opensearch.index(index=chunk.index_name, body=data, id=chunk.key)

    return {"status_code": 200, "status": "success", "message": "청크 색인 성공"}


@app.post("/app/dpr_search/")
def dpr_search(chunk: Chunk):
    response = opensearch.delete(index=chunk.index_name, id=chunk.key)
    return {"status_code": 200, "status": "success", "message": "청크 삭제 성공"}


@app.post("/app/bm25_search/")
def bm25_search(chunk: Chunk):
    response = opensearch.delete(index=chunk.index_name, id=chunk.key)
    return {"status_code": 200, "status": "success", "message": "청크 삭제 성공"}


if __name__ == "__main__":
    response = create_index(Name(name="test"))
    response = index_chunk(
        Chunk(
            index_name="test",
            content="예제입니다",
            key=1,
        )
    )
    response = delete_chunk(
        Chunk(
            index_name="test",
            content="예제입니다",
            key=1,
        )
    )
    response = delete_index(Name(name="test"))
    # breakpoint()

    pass
