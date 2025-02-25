from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from typing import Optional

from fiap_datathon_app.ml.recommendation import NewsRecommender

import json
import os

import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# --- Configuration ---
API_TOKEN = os.getenv("API_TOKEN", "your_default_api_token") # Default API token, CHANGE THIS!

INITIALIZE_QDRANT = bool(os.getenv("INITIALIZE_QDRANT", "0"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "news_collection")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-distilroberta-v1")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
QDRANT_UPLOAD_BATCH_SIZE= int(os.getenv("QDRANT_UPLOAD_BATCH_SIZE", "100"))
TRUNCATION_MAX_LENGTH=int(os.getenv("TRUNCATION_MAX_LENGTH", "512"))
USE_GPU = bool(os.getenv("USE_GPU", "1"))

news_recommender = NewsRecommender(    
        collection_name=QDRANT_COLLECTION_NAME,
        embedding_model=EMBEDDING_MODEL,
        qdrant_host=QDRANT_HOST,
        embedding_batch_size=EMBEDDING_BATCH_SIZE,
        qdrant_upload_batch_size=QDRANT_UPLOAD_BATCH_SIZE,
        truncation_max_length=TRUNCATION_MAX_LENGTH,
        use_gpu=USE_GPU,
        new_qdrant_collection=INITIALIZE_QDRANT     
    )

# --- Data Model ---
class Recommendation(BaseModel):
    viewed_news: list[str]
    init_time: str
    end_time: str
    top_n: Optional[int] = 1
    news_text: Optional[bool] = False

class News(BaseModel):
    page: str
    body: str
    issued: str

class NewsList(BaseModel):
    news_list: list[News]

# --- Security Dependency ---
async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme. Use Bearer.")
        if token != API_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid token")
        return True
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

# --- FastAPI App ---
app = FastAPI(title="Event Ingestion API", description="Receives events and sends them to Kafka")

@app.post("/recommendation/", dependencies=[Depends(verify_token)])
async def news_recommendation(request: Request, recommendation_data: Recommendation):
    try:
        rec_dict = recommendation_data.model_dump()

        recommendation = news_recommender.recommend_news(
                viewed_news_urls = rec_dict['viewed_news'], 
                init_time= rec_dict['init_time'], 
                end_time= rec_dict['end_time'],
                top_n=rec_dict['top_n'],
                news_text = rec_dict['news_text']

            )

        return {"status": "success", "recommended_news": recommendation}
    except Exception as e:
        logging.info(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to infer")


@app.post("/add_news/", dependencies=[Depends(verify_token)])
async def add_news(request: Request, news_list: NewsList):
    try:
        news_dict = news_list.model_dump()

        add_news_return = news_recommender.add_news(news_dict['news_list'])
        return {"status": "success", "values": add_news_return}
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail="Failed to add")

@app.get("/health/")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "OK"}