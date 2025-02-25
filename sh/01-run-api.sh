export INITIALIZE_QDRANT=0
export API_TOKEN="dsafadsflkfjgoirvklvfdiodrjfodflk"

uvicorn fiap_datathon_app.api:app --reload --host 0.0.0.0 --port 8000