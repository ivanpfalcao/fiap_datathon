BASEDIR="$( cd "$( dirname "${0}" )" && pwd )"

pushd ${BASEDIR}/..
pip install .
popd 