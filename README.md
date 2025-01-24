# OpenSearch

- ElasticSearch 7.0 에서 Fork
- **주의사항**: 형태소 분석 기능은 다른 repo에 파두겠습니다.
    - Mecab같은 형태소 분석기가 설치할때 번거롭고, 
    - 컨테이너 띄울때 오래 걸려서 기능을 분리해두었습니다.
- 벡터 검색(WIP), BM25 검색(WIP), 앙상블 검색(WIP)


# 설치

```
pip install -r requirements.txt
bash scripts/create.sh 
```

# Custom

- **IP/PORT 설정 필수**
- scripts/*.sh 파일들 내의 포트
- .env파일의 오픈서치 비밀번호
- scripts/opensearch.sh내의 gpu수
- main.py의 EMB(임베딩 모델)
- **대쉬보드는 포트 변경이 안되는 것 같아요**
- ...etc


# 사용

## 키바나 대쉬보드
- http://<your_ip>:<your_port>/app/login?nextUrl=%2F

에서 확인 가능합니다.

## API 실행

```
bash scripts/opensearch.sh 
```

