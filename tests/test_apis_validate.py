#!/usr/bin/env python
"""Tests for `alertlogic-sdk-definitions` package."""

import unittest
import alsdkdefs


class TestServiceDefs(unittest.TestCase):
    def setUp(self):
        """Setup"""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_validate_definitions(self):
        services = alsdkdefs.list_services()
        for service in services:
            print("Validating ", service)
            for defintion_file in alsdkdefs.get_service_defs(service):
                print("Validating def", defintion_file)
                obj = alsdkdefs.get_spec(alsdkdefs.make_file_uri(defintion_file))
                alsdkdefs.validate(obj, defintion_file)
