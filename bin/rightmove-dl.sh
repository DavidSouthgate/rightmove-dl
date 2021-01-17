#!/bin/sh

if [ ! -d .env ]; then
    source setup-env.sh
else
    source .env/bin/activate
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python "${DIR}/../src/rightmove-dl.py" "$@"