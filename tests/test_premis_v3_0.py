from pathlib import Path

import pytest

from eark_models.premis.v3_0 import Premis

root = Path("tests/sip-examples")
premis_files = root.rglob("premis.xml")


@pytest.mark.parametrize("premis_path", premis_files)
def test_premis_example(premis_path: Path):
    Premis.from_xml(premis_path)
