#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ ! -d "${DIR}/../.env" ]; then
    source "${DIR}/../setup-env.sh"
else
    source "${DIR}/../.env/bin/activate"
fi

python "${DIR}/../src/rightmove-csv.py"