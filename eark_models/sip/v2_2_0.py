from typing import Generic, TypeVar
from pathlib import Path

from pydantic.dataclasses import dataclass

from eark_models.premis.v3_0 import Premis
from eark_models.mets.v1_12_1 import METS
from eark_models.utils import XMLParseable

T = TypeVar("T", bound=XMLParseable)


@dataclass
class PackageMetadata(Generic[T]):
    descriptive: T
    preservation: Premis

    @classmethod
    def from_path(cls, path: Path, descriptive_cls: type[T]) -> "PackageMetadata":
        premis_path = next(path.glob("preservation/premis.xml"))
        descriptive_path = next(path.glob("descriptive/*.xml"))

        return cls(
            descriptive=descriptive_cls.from_xml(descriptive_path),
            preservation=Premis.from_xml(premis_path),
        )


@dataclass
class RepresentationMetadata:
    preservation: Premis

    @classmethod
    def from_path(cls, path: Path) -> "RepresentationMetadata":
        premis_path = next(path.glob("preservation/premis.xml"))
        return cls(preservation=Premis.from_xml(premis_path))


@dataclass
class Representation(Generic[T]):
    path: Path
    mets: METS
    metadata: RepresentationMetadata
    data: list[Path]

    @classmethod
    def from_path(cls, path: Path) -> "Representation":
        mets_path = next(path.glob("METS.xml"))
        metadata_path = next(path.glob("metadata"))
        data_paths = list(path.glob("data/*"))

        return cls(
            path=path,
            mets=METS.from_xml(mets_path),
            metadata=RepresentationMetadata.from_path(metadata_path),
            data=data_paths,
        )


@dataclass
class SIP(Generic[T]):
    unzipped_path: Path
    mets: METS
    metadata: PackageMetadata[T]
    representations: list[Representation[T]]

    @classmethod
    def from_path(cls, unzipped_path: Path, descriptive_cls: type[T]) -> "SIP":
        mets_path = next(unzipped_path.glob("METS.xml"))
        metadata_path = next(unzipped_path.glob("metadata"))
        representations_paths = unzipped_path.glob("representations/*")

        return cls(
            unzipped_path=unzipped_path,
            mets=METS.from_xml(mets_path),
            metadata=PackageMetadata.from_path(metadata_path, descriptive_cls),
            representations=[
                Representation.from_path(p) for p in representations_paths
            ],
        )
