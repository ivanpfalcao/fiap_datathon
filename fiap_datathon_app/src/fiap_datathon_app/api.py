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


news_recommender = NewsRecommender()

# --- Data Model ---
class Recommendation(BaseModel):
    viewed_news: list[str]
    init_time: str
    end_time: str
    top_n: Optional[int] = 1
    news_text: Optional[bool] = False


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
        print(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to infer")


@app.get("/health/")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "OK"}