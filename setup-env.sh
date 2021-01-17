#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 -m venv ${DIR}/.env
. ${DIR}/.env/bin/activate
pip install -r ${DIR}/requirements.txt