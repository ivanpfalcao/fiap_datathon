BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

export DATA_PREP_OUTPUT_FOLDER="${BASEDIR}/../output"
export API_KEY="dsafadsflkfjgoirvklvfdiodrjfodflk"
export API_URL="http://127.0.0.1:8000/recommendation/"

export INIT_INDEX="100"
export END_INDEX="200"

export NUMBER_OF_DAYS_BEFORE="45"
export NUMBER_OF_DAYS_AFTER="1"

export TOP_N="2"
export NEWS_TEXT="1"

export MAX_NEWS_TO_INFER=2

mkdir -p "${DATA_PREP_OUTPUT_FOLDER}"

python -m fiap_datathon_app.inference_test