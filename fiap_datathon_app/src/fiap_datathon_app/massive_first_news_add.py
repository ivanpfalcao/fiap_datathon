import os

from fiap_datathon_app.data.globo import *

DATA_PREP_OUTPUT_FOLDER = os.getenv("INPUT_FIRST_NEWS_FILE")
API_URL = os.getenv("FIRST_NEWS_API_URL")
API_KEY = os.getenv("API_KEY")


gb = GloboData(DATA_PREP_OUTPUT_FOLDER)

gb.add_first_news_from_dataframe(
    input_file = DATA_PREP_OUTPUT_FOLDER
    , url = API_URL
    , api_key = API_KEY
    , news_per_request=10

)