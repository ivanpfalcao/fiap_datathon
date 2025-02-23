export INITIALIZE_QDRANT=0
export API_KEY="dsafadsflkfjgoirvklvfdiodrjfodflk"

uvicorn fiap_datathon_app.api:app --reload --host 0.0.0.0 --port 8000