from pathlib import Path

import pytest

from eark_models.mods.v3_7 import Mods
from eark_models.utils import parse_xml_tree

from tests.utils import count_object_contents, count_xml_contents

root = Path("tests/sip-examples")
mods_files = list(root.rglob("mods.xml"))


@pytest.mark.parametrize("mods_path", mods_files)
def test_mods_example_parsing(mods_path: Path):
    Mods.from_xml(mods_path)


@pytest.mark.parametrize("mods_path", mods_files)
def test_mods_example_completeness(mods_path: Path):
    root = parse_xml_tree(mods_path)
    mods = Mods.from_xml(mods_path)
    assert count_object_contents(mods) == count_xml_contents(root)
