BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

export DATA_PREP_OUTPUT_FOLDER="${BASEDIR}/../output"
export INPUT_FIRST_NEWS_FILE="${DATA_PREP_OUTPUT_FOLDER}/first_news.parquet"

export API_KEY="dsafadsflkfjgoirvklvfdiodrjfodflk"
export FIRST_NEWS_API_URL="http://127.0.0.1:8000/add_first_news/"

python -m fiap_datathon_app.massive_first_news_add