import numpy as np
import torch
import torch.nn.functional as F
import uuid
import logging
import duckdb
import re
from tqdm import tqdm
from datetime import datetime, timedelta, timezone

import nltk
from nltk.corpus import stopwords

from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, PointStruct, CollectionParams
from qdrant_client.http.models import HnswConfigDiff
from huggingface_hub import login


class NewsRecommender:
        def __init__(
            self,
            collection_name="news_collection",
            embedding_model="sentence-transformers/all-distilroberta-v1",
            qdrant_host="http://localhost:6333",
            embedding_batch_size=100,
            qdrant_upload_batch_size=100,
            use_gpu=True,
            top_n = 5,
            max_hist = 5          
        ):
                """
                Initializes the NewsRecommender.

                Args:
                collection_name: The name of the Qdrant collection.
                embedding_model: The name/path of the huggingface model to be used for embeddings.
                qdrant_host: The host for the Qdrant client.
                embedding_batch_size: The size of each batch when encoding sentences.
                qdrant_upload_batch_size: The size of each batch when uploading to Qdrant.
                use_gpu: Move model and data to GPU if True.
                """

                self.embedding_model = embedding_model
                
                self.embedding_batch_size = embedding_batch_size
                self.qdrant_upload_batch_size = qdrant_upload_batch_size
                self.use_gpu = use_gpu

                self.collection_name = collection_name 

                self.model = None

                self.qdrant_host = qdrant_host
                self.qdrant_client = None
                self.top_n = top_n
                self.max_hist = max_hist

                if self.qdrant_host == ":memory:":
                    self.qdrant_client = QdrantClient(location=self.qdrant_host, timeout=100000)
                else:
                    self.qdrant_client = QdrantClient(url=self.qdrant_host, timeout=100000)  



        def load_model(self):
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.embedding_model)
                self.model = AutoModel.from_pretrained(self.embedding_model)

                # Ensure the tokenizer has a padding token
                if not self.tokenizer.pad_token:
                    if self.tokenizer.eos_token:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                else:
                    self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                    self.model.resize_token_embeddings(len(self.tokenizer))

                # If GPU is available and use_gpu is True, move model to CUDA
                self.device = "cuda" if (torch.cuda.is_available() and self.use_gpu) else "cpu"
                self.model.to(self.device)

        def hash_url_to_string(self, url):
            """
            Hashes a URL to its full hexadecimal string representation.
            """
            return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        
        def recommend_news(
            self,
            viewed_news_urls: list,
            init_time: str,
            end_time: str,
            top_n=10,
            news_text = False
        ):
            if len(viewed_news_urls) == 0:
                return []

            viewed_news_hashes = [self.hash_url_to_string(url) for url in viewed_news_urls]

            # Retrieve each viewed news vector
            viewed_news = self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=viewed_news_hashes,
                with_vectors=True
            )

            logging.info(f'Viewed news items requested: {len(viewed_news_hashes)}')
            if not viewed_news:
                logging.warning("No viewed news vectors found. Returning empty list.")
                return []
            else:
                logging.info(f"Retrieved vectors for viewed news: {len(viewed_news)}")

            init_ts = int(datetime.strptime(init_time, '%Y-%m-%dT%H:%M:%SZ').timestamp())
            end_ts = int(datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ').timestamp())

            # We'll store all top_n results from each historical news in one concatenated list
            
            full_recom = {}
            for idx, news_item in enumerate(viewed_news):
                all_recommendations = []
                if not news_item or not news_item.vector:
                    continue
                
                news_vector = news_item.vector

                search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=news_vector,
                search_params=models.SearchParams(hnsw_ef=4096, exact=False),
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="news_date",
                            range=models.Range(
                                gte=init_ts,
                                lte=end_ts
                            )
                        )
                    ],
                    must_not=[
                        models.FieldCondition(
                            key="original_url",
                            match=models.MatchValue(value=url)
                        ) for url in viewed_news_urls
                    ]
                ),
                limit=top_n
                )
                
                for r in search_result:
                    viewed_news_urls.append(r.payload["original_url"])

                    recommendation = {
                         "original_url": r.payload["original_url"],
                    }

                    if news_text:
                        recommendation['text'] = r.payload["text"]
                    all_recommendations.append(recommendation)


                recom_dict = {                     
                    'recommendations': all_recommendations
                }

                if news_text:
                    recom_dict['text'] = news_item.payload["text"] 

                full_recom[news_item.payload['original_url']] = recom_dict

            return full_recom                                