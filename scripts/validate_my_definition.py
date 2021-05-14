#!/usr/bin/env python3

from yaml import YAMLError
from jsonschema.exceptions import ValidationError, RefResolutionError
from argparse import ArgumentParser
import glob
from alsdkdefs import AlertLogicOpenApiValidationException
import alsdkdefs
import os


def validate_definition(definition_file):
    print(f"Validating {definition_file}")
    try:
        uri_or_path = alsdkdefs.normalize_uri(definition_file)
        # Validate raw
        spec = alsdkdefs.get_spec(uri_or_path)
        alsdkdefs.validate(spec, uri_or_path)
        # Then validate normalised
        spec = alsdkdefs.load_spec(uri_or_path)
        alsdkdefs.validate(spec, uri_or_path)
    except YAMLError as e:
        print(f"Validation has failed - failed to load YAML {e}")
        exit(1)
    except ValidationError as e:
        print(f"Validation has failed - schema validation has failed {e}")
        exit(1)
    except RefResolutionError as e:
        print(f"Validation has failed - $ref resolution has failed {e}")
        exit(1)
    except AlertLogicOpenApiValidationException as e:
        print(f"Validation has failed - definition has failed AlertLogic specific check {e}")
        exit(1)
    except TypeError:
        print(f"Validation has failed - json schema trips over integer keys, please "
              f"validate your response codes are not integers, check also other keys are not integers"
              f"if any of it are, quote it, '200', '400' etc")
        exit(1)
    print("Validation passed")


if __name__ == "__main__":
    parser = ArgumentParser(description="Validates OpenAPI YAML developed for Alert Logic SDK")
    parser.add_argument("-d", "--definitions_directory", dest="dir", default="doc/openapi/",
                        help="Directory with definitions to test")
    options = parser.parse_args()
    if os.path.isabs(options.dir):
        search_dir = options.dir
    else:
        search_dir = os.path.abspath(options.dir)
    search_pattern = os.path.join(search_dir, '*.v[1-9]*.yaml')
    files = glob.glob(search_pattern)
    if files:
        for file in files:
            validate_definition(file)
    else:
        print(f"No definitions found at {options.dir} skip validation")
