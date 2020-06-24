#!/usr/bin/env python3

import jsonschema
import yaml
from yaml import YAMLError
from jsonschema.exceptions import ValidationError
import requests
from argparse import ArgumentParser

OPENAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/schemas/v3.0/schema.json'

if __name__ == "__main__":
    parser = ArgumentParser(description="Validates OpenAPI YAML developed for Alert Logic SDK")
    parser.add_argument("-f", "--definition_file", dest="definition", required=True,
                        help="Filename of a definition to test")
    options = parser.parse_args()
    r = requests.get(OPENAPI_SCHEMA_URL)
    schema = r.json()
    with open(options.definition, "r") as f:
        spec = f.read()
    if spec:
        try:
            obj = yaml.load(spec, Loader=yaml.SafeLoader)
            jsonschema.validate(obj, schema)
        except YAMLError as e:
            print(f"Validation has failed - failed to load YAML {e}")
            exit(1)
        except ValidationError as e:
            print(f"Validation has failed - schema validation has failed {e}")
            exit(1)
        print("Validation passed")
    else:
        print("Input is empty")
        exit(1)
