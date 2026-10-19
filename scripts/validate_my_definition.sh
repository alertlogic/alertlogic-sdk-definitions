#!/usr/bin/env bash
set -e

export TEMP=$(mktemp -d -t alertlogic-sdk-definitions-validation-XXXX)

if [ -n "$AL_SDK_VALIDATE_PYTHON" ]; then
  PYTHON="$AL_SDK_VALIDATE_PYTHON"
elif command -v python3.15; then
  PYTHON=python3.15
elif command -v python3.14; then
  PYTHON=python3.14
elif command -v python3.13; then
  PYTHON=python3.13
elif command -v python3.12; then
  PYTHON=python3.12
elif command -v python3.11; then
  PYTHON=python3.11
elif command -v python3; then
  PYTHON=python3
else
  echo "No suitable python3 interpreter is found"
  exit 1
fi

echo "OpenAPI validation using python: $PYTHON"
$PYTHON --version
$PYTHON -m venv $TEMP
source $TEMP/bin/activate
pip3 install alertlogic-sdk-definitions --no-cache-dir --ignore-requires-python
curl https://raw.githubusercontent.com/alertlogic/alertlogic-sdk-definitions/master/scripts/validate_my_definition.py -o $TEMP/validate_my_definition.py
if [ $# -eq 0 ]
then
  $PYTHON $TEMP/validate_my_definition.py && rm -rf $TEMP
else
  $PYTHON $TEMP/validate_my_definition.py -d $1 && rm -rf $TEMP
fi
