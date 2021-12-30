#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )" 
export PYTHONPATH="$SCRIPTPATH/../.."
. $PYTHONPATH/bin/activate

cd $SCRIPTPATH
python ./main.py
