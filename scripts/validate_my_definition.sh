#!/usr/bin/env bash
set +e

export TEMP=$(mktemp -d -t alertlogic-sdk-definitions-validation-XXXX)

if python3 -m venv $TEMP; then
  source $TEMP/bin/activate
  pip3 install requests jsonschema PyYaml
  curl https://raw.githubusercontent.com/alertlogic/alertlogic-sdk-definitions/master/scripts/validate_my_definition.py -o $TEMP/validate_my_definition.py
  if [ $# -eq 0 ]
  then
    python3 $TEMP/validate_my_definition.py && rm -rf $TEMP
  else
    python3 $TEMP/validate_my_definition.py -d $1 && rm -rf $TEMP
  fi
fi