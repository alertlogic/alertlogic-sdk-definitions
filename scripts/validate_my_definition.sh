#!/usr/bin/env bash
set +e

export TEMP=$(mktemp -d -t alertlogic-sdk-definitions-validation-XXXX)

if command -v python3.8; then
  PYTHON=python3.8
elif command -v python3.7; then
  PYTHON=python3.7
elif command -v python3.6; then
  PYTHON=python3.6
elif command -v python3; then
  PYTHON=python3
else
  echo "No suitable python3 interpreter is found"
  exit 1
fi

if $PYTHON -m venv $TEMP; then
  source $TEMP/bin/activate
  pip3 install alertlogic-sdk-definitions --no-cache-dir --ignore-requires-python
  curl https://raw.githubusercontent.com/alertlogic/alertlogic-sdk-definitions/master/scripts/validate_my_definition.py -o $TEMP/validate_my_definition.py
  if [ $# -eq 0 ]
  then
    $PYTHON $TEMP/validate_my_definition.py && rm -rf $TEMP
  else
    $PYTHON $TEMP/validate_my_definition.py -d $1 && rm -rf $TEMP
  fi
fi
