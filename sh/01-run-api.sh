export INITIALIZE_QDRANT=0
export API_TOKEN="dsafadsflkfjgoirvklvfdiodrjfodflk"
export QDRANT_COLLECTION_NAME="news_collection"
export EMBEDDING_MODEL"sentence-transformers/all-distilroberta-v1"
export QDRANT_HOST"http://localhost:6333"
export EMBEDDING_BATCH_SIZE"100"
export QDRANT_UPLOAD_BATCH_SIZE="100"
export TRUNCATION_MAX_LENGTH="512"
export USE_GPU="1"

uvicorn fiap_datathon_app.api:app --reload --host 0.0.0.0 --port 8000