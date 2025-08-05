from pathlib import Path

import pytest

from eark_models.dc_schema.v2_1 import DCPlusSchema
from eark_models.utils import parse_xml_tree

from tests.utils import count_object_contents, count_xml_contents

root = Path("tests/sip-examples/2.1")
dc_schema_files = list(root.rglob("dc+schema.xml"))


@pytest.mark.parametrize("dc_schema_path", dc_schema_files)
def test_dc_schema_example_parsing(dc_schema_path: Path):
    DCPlusSchema.from_xml(dc_schema_path)


@pytest.mark.parametrize("dc_schema_path", dc_schema_files)
def test_dc_schema_example_completeness(dc_schema_path: Path):
    root = parse_xml_tree(dc_schema_path)
    dc_schema = DCPlusSchema.from_xml(dc_schema_path)
    assert count_object_contents(dc_schema) == count_xml_contents(root)


def test_dc_schema_sample_parsing():
    path = Path("tests/dc_schema/v2_1/samples/sample_01.xml")
    _ = DCPlusSchema.from_xml(path)


def test_dc_schema_sample_completeness():
    path = Path("tests/dc_schema/v2_1/samples/sample_01.xml")
    root = parse_xml_tree(path)
    dc_schema = DCPlusSchema.from_xml(path)
    assert count_object_contents(dc_schema) == count_xml_contents(root)
