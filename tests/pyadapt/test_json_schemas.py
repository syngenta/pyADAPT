import json
from pathlib import Path
from unittest import TestCase

import pyadapt.schemas as schemas

TEST_OPERATION_FILENAME = "5293be65-d49e-5a53-8328-83a5b8e057f3-summary.json"


class TestJsonSchemaValidation(TestCase):
    def test_validate_operation(self):
        with (Path(__file__).parent / TEST_OPERATION_FILENAME).open("r") as file:
            test_summary = json.load(file)
        schemas.validate(test_summary, "Operation")
