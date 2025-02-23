import os

from fiap_datathon_app.data.globo import *

DATA_PREP_OUTPUT_FOLDER = os.getenv("DATA_PREP_OUTPUT_FOLDER")
DATA_PREP_ITEMS_FOLDER = os.getenv("DATA_PREP_ITEMS_FOLDER")
DATA_PREP_TREINO_FOLDER = os.getenv("DATA_PREP_TREINO_FOLDER")


gb = GloboData(DATA_PREP_OUTPUT_FOLDER)

gb.prepare_itens(DATA_PREP_ITEMS_FOLDER)
gb.prepare_treino(DATA_PREP_TREINO_FOLDER)
gb.prep_reduced_itens()