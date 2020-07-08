#!/usr/bin/env python3

import jsonschema
import yaml
from yaml import YAMLError
from jsonschema.exceptions import ValidationError
import requests
from argparse import ArgumentParser
import glob
from almdrlib.client import _YamlOrderedLoader
OPENAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/schemas/v3.0/schema.json'


def validate_definition(definition_file):
    print(f"Validating {definition_file}")
    with open(definition_file, "r") as f:
        spec = f.read()
    if spec:
        try:
            obj = yaml.load(spec, Loader=_YamlOrderedLoader)
            jsonschema.validate(obj, schema)
        except YAMLError as e:
            print(f"Validation has failed - failed to load YAML {e}")
            exit(1)
        except ValidationError as e:
            print(f"Validation has failed - schema validation has failed {e}")
            exit(1)
        except TypeError:
            print(f"Validation has failed - json schema trips over integer keys, please "
                  f"validate your response codes are not integers, check also other keys are not integers"
                  f"if any of it are, quote it, '200', '400' etc")
            exit(1)
        print("Validation passed")
    else:
        print("Input is empty")
        exit(1)


if __name__ == "__main__":
    parser = ArgumentParser(description="Validates OpenAPI YAML developed for Alert Logic SDK")
    parser.add_argument("-d", "--definitions_directory", dest="dir", default="doc/openapi/",
                        help="Directory with definitions to test")
    options = parser.parse_args()
    r = requests.get(OPENAPI_SCHEMA_URL)
    schema = r.json()
    files = glob.glob(f"{options.dir}/*.v[1-9]*.yaml")
    if files:
        for file in files:
            validate_definition(file)
    else:
        print(f"No definitions found at {options.dir} skip validation")
