import requests
import json
import os
from fiap_datathon_app.data.globo import *

DATA_PREP_OUTPUT_FOLDER = os.getenv("DATA_PREP_OUTPUT_FOLDER")
INPUT_INF_FILE = os.getenv("INPUT_INF_FILE", None)
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

INIT_INDEX = int(os.getenv("INIT_INDEX", 0))
END_INDEX = int(os.getenv("END_INDEX", 10))

NUMBER_OF_DAYS_BEFORE = int(os.getenv("NUMBER_OF_DAYS_BEFORE", 45))
NUMBER_OF_DAYS_AFTER = int(os.getenv("NUMBER_OF_DAYS_BEFORE", 1))

TOP_N = int(os.getenv("TOP_N", 2))
NEWS_TEXT = bool(os.getenv("NEWS_TEXT", 0))

MAX_NEWS_TO_INFER = int(os.getenv("MAX_NEWS_TO_INFER", 5))

gb = GloboData(DATA_PREP_OUTPUT_FOLDER)

gb.massive_inference_tests(
    opt_input_file=INPUT_INF_FILE
    , init_index = INIT_INDEX
    , end_index = END_INDEX
    , url=API_URL
    , api_key=API_KEY
    , number_of_days_before = NUMBER_OF_DAYS_BEFORE
    , number_of_days_after = NUMBER_OF_DAYS_AFTER
    , top_n = TOP_N
    , news_text = NEWS_TEXT
    , max_news_to_infer = MAX_NEWS_TO_INFER
)