#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "${DIR}" )"
LIB_DIR="${PROJECT_DIR}/lib"

mkdir -p "${LIB_DIR}"

pushd "${LIB_DIR}"
    git clone https://github.com/josiah-wolf-oberholtzer/supriya.git
    cd supriya
    pip3 install -e .
popd
