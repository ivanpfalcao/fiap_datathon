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

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

class NewsRecommender:
        def __init__(
            self,
            collection_name="news_collection",
            embedding_model="sentence-transformers/all-distilroberta-v1",
            qdrant_host="http://localhost:6333",
            embedding_batch_size=100,
            qdrant_upload_batch_size=100,
            truncation_max_length = 512,
            use_gpu=True,
            top_n = 5,
            max_hist = 5,
            new_qdrant_collection = False     
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
                self.truncation_max_length = truncation_max_length

                if self.qdrant_host == ":memory:":
                    self.qdrant_client = QdrantClient(location=self.qdrant_host, timeout=100000)
                else:
                    self.qdrant_client = QdrantClient(url=self.qdrant_host, timeout=100000)

                if (self.model is None):
                    self.load_model()

                self.embedding_dim = self.model.config.hidden_size

                logging.info(f"Initializing Qdrant: {new_qdrant_collection}")
                if (new_qdrant_collection):
                    self._create_collection()                    


        def _create_collection(self):

            try:
                logging.info(f"Getting collection {self.collection_name}")
                logging.info(f"Qdrant collection size: {self.embedding_dim}")
                self.qdrant_client.get_collection(self.collection_name)
            except:
                logging.info(f"Collection doesn´t exist. Creating collection {self.collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    ),
                    hnsw_config=models.HnswConfigDiff(
                        m=2048,
                        ef_construct=4096,
                        full_scan_threshold=500
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=50000,
                        max_segment_size=100000,
                        memmap_threshold=200000
                    ),
                )

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

        def mean_pooling(self, model_output, attention_mask):
            """
            Mean Pooling - Take attention mask into account for correct averaging.
            """
            token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


        def _encode_sentences_in_batches(self, sentences, max_length):
            if (self.model is None):
                  self.load_model()

            all_embeddings = []
            total_batches = (len(sentences) + self.embedding_batch_size - 1) // self.embedding_batch_size

            for start_idx in tqdm(range(0, len(sentences), self.embedding_batch_size), total=total_batches, desc="Embedding Sentences"):
                batch_texts = sentences[start_idx : start_idx + self.embedding_batch_size]

                encoded_input = self.tokenizer(
                   batch_texts,
                   padding=True,
                   truncation=True,
                   max_length=max_length,
                   return_tensors='pt'
                ).to(self.device)

                with torch.no_grad(), torch.cuda.amp.autocast():  # Mixed precision
                   model_output = self.model(**encoded_input)

                batch_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
                batch_embeddings = F.normalize(batch_embeddings, p=2, dim=1)

                all_embeddings.append(batch_embeddings.cpu())
                torch.cuda.empty_cache()  # Clear cache to free memory

            return torch.cat(all_embeddings, dim=0).numpy().tolist()

        def clean_text(self, text):
            """
            Perform basic text cleaning steps:
            1. (Optionally) Remove HTML tags
            2. (Optionally) Convert to lowercase
            3. (Optionally) Remove extra whitespace
            4. (Optionally) Remove URLs or other patterns
            5. (Optionally) Remove punctuation or special characters
            Customize this function as needed.
            """
            if not isinstance(text, str):
                return ""
            # You can uncomment or adapt cleaning steps as needed
            # cleaned = re.sub(r"<.*?>", "", text)
            # cleaned = cleaned.lower()
            # cleaned = re.sub(r"http\S+|www\S+|https\S+", "", text)
            # cleaned = re.sub(r"\s+", " ", cleaned).strip()
            # cleaned = re.sub(r"[^a-zA-ZÀ-ÖÙ-öù-ÿ0-9\s.,;:!?-]", "", text)
            # cleaned = remove_pt_stopwords(cleaned)
            return text

        def qdrant_batch_upsert(self, collection_name, points, batch_size):
            if (self.model is None):
                self.load_model()

            if (self.qdrant_client is None):
                self.embedding_dim = self.model.config.hidden_size
                self._create_collection()

    
            logging.info(f"Batch loading data into Qdrant collection {collection_name}. Batch size: {batch_size}")
            for i in range(0, len(points), batch_size):
                try:
                    batch = points[i : i + batch_size]
                    self.qdrant_client.upsert(collection_name=collection_name, points=batch)
                except Exception as e:
                    logging.info(f"Error: {e}. Continuing")


        def add_news(self, add_news_list: list[dict]):
            """
            Adds news articles to the Qdrant database.
            Expects 'page' (URL), 'body' (text), and 'issued' (date) columns.
            """

            logging.info(f"Hashing page URL")
            clean_text_list = []
            for i in range(len(add_news_list)):
                cleaned_news = self.clean_text(add_news_list[i]["body"])
                add_news_list[i]["clean_text"] = cleaned_news
                add_news_list[i]['hash_str'] = self.hash_url_to_string(add_news_list[i]['page'])

                clean_text_list.append(cleaned_news)


            logging.info(f"Starting embeddings generation")

            embeddings = self._encode_sentences_in_batches(clean_text_list, self.truncation_max_length)
            logging.info(f"Embeddings generation completed")

            points = []

            news_hash_list = []
            for i in range(len(add_news_list)):
                point_id = add_news_list[i]['hash_str']
                point_vector = embeddings[i]
                payload = {
                   "text": add_news_list[i]['clean_text'],
                   "original_url": add_news_list[i]['page'],
                   #"news_date": int(add_news_list[i]['issued'].timestamp())
                   "news_date": datetime.fromisoformat(add_news_list[i]['issued'].replace('Z', '-03:00')).timestamp()

                   
                }
                points.append(PointStruct(id=point_id, vector=point_vector, payload=payload))

                news_hash_list.append({
                    "original_url": add_news_list[i]['page'],
                    "hashed_url": add_news_list[i]['hash_str']
                })

            logging.info(f"Starting Qdrant upsert")
            self.qdrant_batch_upsert(collection_name=self.collection_name, points=points, batch_size=self.qdrant_upload_batch_size)
            logging.info(f"Qdrant upsert ended")      

            return news_hash_list                                                   