BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

export DATA_PREP_OUTPUT_FOLDER="${BASEDIR}/../output"
export DATA_PREP_ITEMS_FOLDER="${BASEDIR}/../challenge-webmedia-e-globo-2023/itens/itens/*.csv"
export DATA_PREP_TREINO_FOLDER="${BASEDIR}/../challenge-webmedia-e-globo-2023/files/treino/*.csv"

mkdir -p "$DATA_PREP_OUTPUT_FOLDER"

python -m fiap_datathon_app.data_prep