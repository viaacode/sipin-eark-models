from typing import Self
from pathlib import Path

import pytest
from pydantic.dataclasses import dataclass

from eark_models.sip.v2_2_0 import SIP
from eark_models.utils import XMLBase


@dataclass
class Dummy(XMLBase):
    @classmethod
    def from_xml(cls, path: Path) -> Self:
        return cls()


examples_path = Path("tests/sip-examples")
sip_paths = list(examples_path.joinpath("2.1").iterdir())

# TODO: This sip has not been migrated fully to 2.1
sip_paths = [p for p in sip_paths if "ftp_sidecar" not in str(p)]
unzipped_paths = [next(path.iterdir()) for path in sip_paths]


@pytest.mark.parametrize("unzipped_path", unzipped_paths)
def test_sip_example_parsing(unzipped_path: Path):
    SIP[Dummy].from_path(unzipped_path, Dummy)
