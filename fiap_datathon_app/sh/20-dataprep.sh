BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

export DATA_PREP_OUTPUT_FOLDER="/mnt/c/projects/fiap-datathon/fiap_datathon_app/sh/output"
export DATA_PREP_ITEMS_FOLDER="/mnt/c/projects/fiap-datathon-dev/challenge-webmedia-e-globo-2023/itens/itens/*.csv"
export DATA_PREP_TREINO_FOLDER="/mnt/c/projects/fiap-datathon-dev/challenge-webmedia-e-globo-2023/files/treino/*.csv"

python -m fiap_datathon_app.data_prep