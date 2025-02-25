# Define the base directory relative to the script location
BASEDIR=$(cd -P -- "$(dirname -- "${0}")" && pwd -P)


pushd "${BASEDIR}"
docker build \
    -f news-recomender.dockerfile \
    -t "ivanpfalcao/news-recomender:1.0.0" \
    --progress=plain \
    ..
popd