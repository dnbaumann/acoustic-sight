#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "${DIR}" )"
LIB_DIR="${PROJECT_DIR}/lib"

mkdir -p "${LIB_DIR}"

pushd "${LIB_DIR}"
    git clone https://github.com/pathak22/pyflow.git
    cd pyflow/

    python3 setup.py build_ext -i
    python3 demo.py

    pip3 install -e .
popd
