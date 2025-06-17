from pathlib import Path

import pytest

from eark_models.mods import Mods

root = Path("tests/sip-examples")
mods_files = root.rglob("mods.xml")


@pytest.mark.parametrize("mods_path", mods_files)
def test_mods_example(mods_path: Path):
    Mods.from_xml(mods_path)
