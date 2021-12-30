#!/bin/sh

(
    # We run stylechecks from this file location (presumably root).
    # TODO(billy): Only check git staged files.
    cd "$(dirname "$0")"
    py_files=$(find . -name '*.py')
    pipenv run pycodestyle --show-source $py_files | less
)
