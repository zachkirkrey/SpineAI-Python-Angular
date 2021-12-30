#!/bin/bash

# Run all unit tests in the project.
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH
export PYTHON_CONFIG_DIR="${SCRIPTPATH}/config"
poetry run python -m nose --nologcapture --with-coverage --cover-package=lib --cover-package=runtime
