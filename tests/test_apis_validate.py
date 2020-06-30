#!/usr/bin/env python
"""Tests for `alertlogic-sdk-definitions` package."""


import requests
import jsonschema
import yaml
import unittest
import alsdkdefs
from almdrlib.client import _YamlOrderedLoader

OPENAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/schemas/v3.0/schema.json'


class TestServiceDefs(unittest.TestCase):

    def setUp(self):
        """Setup"""
        r = requests.get(OPENAPI_SCHEMA_URL)
        self.schema = r.json()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_validate_definitions(self):
        services = alsdkdefs.list_services()
        for service in services:
            print("Validating ", service)
            for definition in alsdkdefs.get_service_defs(service):
                print("Validating def", definition)
                with open(definition, 'r') as f:
                    spec = f.read()
                    obj = yaml.load(spec, Loader=_YamlOrderedLoader)
                    jsonschema.validate(obj, self.schema)
