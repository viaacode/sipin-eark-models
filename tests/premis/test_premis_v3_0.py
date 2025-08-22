from pathlib import Path

import pytest

from eark_models.premis.v3_0 import Premis
from eark_models.utils import parse_xml_tree

from tests.utils import count_object_contents, count_xml_contents

root = Path("tests/sip-examples")
premis_files = list(root.rglob("premis.xml"))


@pytest.mark.parametrize("premis_path", premis_files)
def test_premis_example_parsing(premis_path: Path):
    Premis.from_xml(premis_path)


@pytest.mark.parametrize("premis_path", premis_files)
def test_premis_example_completeness(premis_path: Path):
    root = parse_xml_tree(premis_path)
    premis = Premis.from_xml(premis_path)
    assert count_object_contents(premis) == count_xml_contents(root)
