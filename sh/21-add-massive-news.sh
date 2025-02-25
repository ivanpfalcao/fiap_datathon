BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

export DATA_PREP_OUTPUT_FOLDER="${BASEDIR}/../output"
export INPUT_ITEMS_FILE="${DATA_PREP_OUTPUT_FOLDER}/reduced_itens.parquet"

export API_KEY="dsafadsflkfjgoirvklvfdiodrjfodflk"
export API_URL="http://127.0.0.1:8000/add_news/"

python -m fiap_datathon_app.massive_news_add