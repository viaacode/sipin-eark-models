from typing import Self
from pathlib import Path

from pydantic.dataclasses import dataclass


@dataclass
class METS:
    @classmethod
    def from_xml(cls, path: Path | str) -> Self:
        return cls()
