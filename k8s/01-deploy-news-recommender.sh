# Define the base directory relative to the script location
BASEDIR=$(cd -P -- "$(dirname -- "${0}")" && pwd -P)

NAMESPACE="news-recommender-ns"

kubectl create namespace ${NAMESPACE}

kubectl -n ${NAMESPACE} apply -f "${BASEDIR}/news-recommender-dpl.yaml"