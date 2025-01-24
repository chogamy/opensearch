docker build -f "<your_path>"/opensearch/scripts/dockerfile -t opensearch .

docker run -d --gpus '"device=0"' -p 8889:8889 --name opensearch opensearch

rm -rf "<your_path>"/opensearch
