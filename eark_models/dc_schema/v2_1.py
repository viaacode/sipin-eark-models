import typing
from typing import Self, Literal
from pathlib import Path

from dataclasses import field
from pydantic.dataclasses import dataclass

from ..etree import _Element
from ..namespaces import schema, dcterms, xsi
from ..utils import EarkModelsError, InvalidXMLError, XMLParseable, parse_xml_tree

from ..langstring import LangStrings, langstrings, UniqueLang, unique_lang


@dataclass
class EDTF:
    __source__: str = field(compare=False)
    xsi_type: Literal[
        "{http://id.loc.gov/datatypes/edtf/}EDTF-level0",
        "{http://id.loc.gov/datatypes/edtf/}EDTF-level1",
        "{http://id.loc.gov/datatypes/edtf/}EDTF-level2",
    ]
    text: str

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type not in (
            "{http://id.loc.gov/datatypes/edtf/}EDTF-level0",
            "{http://id.loc.gov/datatypes/edtf/}EDTF-level1",
            "{http://id.loc.gov/datatypes/edtf/}EDTF-level2",
        ):
            raise InvalidXMLError("Invalid xsi:type for EDTF.")

        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            text=element.text if element.text is not None else "",
        )


@dataclass
class _Role:
    __source__: str = field(compare=False)

    role_name: str | None
    name: UniqueLang
    birth_date: EDTF | None
    death_date: EDTF | None

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        role_name = element.get(schema.roleName)
        birth_date = element.find(schema.birthDate)
        death_date = element.find(schema.deathDate)
        birth_date = EDTF.from_xml_tree(birth_date) if birth_date is not None else None
        death_date = EDTF.from_xml_tree(death_date) if death_date is not None else None
        return cls(
            __source__=element.__source__,
            name=unique_lang(element, schema.name),
            role_name=role_name,
            birth_date=birth_date,
            death_date=death_date,
        )


class Creator(_Role):
    pass


class Publisher(_Role):
    pass


class Contributor(_Role):
    pass


UnitCode = Literal["MMT", "CMT", "MTR", "KGM"]
UnitText = Literal["mm", "cm", "m", "kg"]


@dataclass
class _Measurement:
    __source__: str = field(compare=False)

    value: str
    unit_code: UnitCode | None
    unit_text: UnitText

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self | None:
        value = get_text(element, schema.value)
        unit_code = element.findtext(schema.unitCode)
        unit_text = get_text(element, schema.unitText)

        if unit_code is not None and unit_code not in ("MMT", "CMT", "MTR", "KGM"):
            raise InvalidXMLError(
                f"Unit code should be one of {typing.get_args(UnitCode)}"
            )
        if unit_text not in ("mm", "cm", "m", "kg"):
            raise InvalidXMLError(
                f"Unit text should be one of {typing.get_args(UnitText)}"
            )

        return cls(
            __source__=element.__source__,
            value=value,
            unit_code=unit_code,
            unit_text=unit_text,
        )


class Height(_Measurement):
    pass


class Width(_Measurement):
    pass


class Depth(_Measurement):
    pass


class Weight(_Measurement):
    pass


CreativeWorkType = Literal[
    schema.Episode,
    schema.ArchiveComponent,
    schema.CreativeWorkSeries,
    schema.CreativeWorkSeason,
]

EventTypes = Literal[schema.BroadcastEvent]


@dataclass
class Episode:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}Episode"]
    name: UniqueLang

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}Episode":
            raise InvalidXMLError()
        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
        )


@dataclass
class HasPartArchiveComponent:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}ArchiveComponent"]
    name: UniqueLang

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}ArchiveComponent":
            raise InvalidXMLError()

        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
        )


@dataclass
class ArchiveComponent:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}ArchiveComponent"]
    name: UniqueLang
    has_part: list[HasPartArchiveComponent]

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}ArchiveComponent":
            raise InvalidXMLError()
        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
            has_part=[
                HasPartArchiveComponent.from_xml_tree(el)
                for el in element.findall(schema.hasPart)
            ],
        )


@dataclass
class HasPartCreativeWorkSeries:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}CreativeWorkSeries"]
    name: UniqueLang

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}CreativeWorkSeries":
            raise InvalidXMLError()

        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
        )


@dataclass
class CreativeWorkSeries:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}CreativeWorkSeries"]
    name: UniqueLang
    position: int | None
    has_part: list[HasPartCreativeWorkSeries]

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        position = element.findtext(schema.position)
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}CreativeWorkSeries":
            raise InvalidXMLError()
        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
            position=int(position) if position else None,
            has_part=[
                HasPartCreativeWorkSeries.from_xml_tree(el)
                for el in element.findall(schema.hasPart)
            ],
        )


@dataclass
class CreativeWorkSeason:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}CreativeWorkSeason"]
    name: UniqueLang
    season_number: int | None

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        season_number = element.findtext(schema.seasonNumber)
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}CreativeWorkSeason":
            raise InvalidXMLError()
        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
            season_number=int(season_number) if season_number else None,
        )


@dataclass
class BroadcastEvent:
    __source__: str = field(compare=False)
    xsi_type: Literal["{https://schema.org/}BroadcastEvent"]
    name: UniqueLang

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        xsi_type = element.get(xsi.type)
        if xsi_type != "{https://schema.org/}BroadcastEvent":
            raise InvalidXMLError()
        return cls(
            __source__=element.__source__,
            xsi_type=xsi_type,
            name=unique_lang(element, schema.name),
        )


AnyCreativeWork = Episode | ArchiveComponent | CreativeWorkSeries | CreativeWorkSeason


def parse_is_part_of(root: _Element) -> AnyCreativeWork | BroadcastEvent:
    type = root.get(xsi.type)

    valid_types = typing.get_args(CreativeWorkType) + typing.get_args(EventTypes)
    if type not in valid_types:
        raise InvalidXMLError(f"schema:isPartOf must be one of {valid_types}")

    match type:
        case schema.Episode:
            return Episode.from_xml_tree(root)
        case schema.ArchiveComponent:
            return ArchiveComponent.from_xml_tree(root)
        case schema.CreativeWorkSeries:
            return CreativeWorkSeries.from_xml_tree(root)
        case schema.CreativeWorkSeason:
            return CreativeWorkSeason.from_xml_tree(root)
        case schema.BroadcastEvent:
            return BroadcastEvent.from_xml_tree(root)
        case _:
            raise EarkModelsError("CreativeWorkType or EventTypes are not complete")


xsd_duration = str
xsd_timedelta = str


@dataclass
class DCPlusSchema(XMLParseable):
    __source__: str = field(compare=False)

    identifier: str
    title: UniqueLang
    alternative: LangStrings
    extent: xsd_duration | None
    available: xsd_timedelta | None
    description: UniqueLang
    abstract: UniqueLang
    created: EDTF
    issued: EDTF | None
    publisher: list[Publisher]
    creator: list[Creator]
    contributor: list[Contributor]
    spatial: list[str]
    temporal: LangStrings
    subject: LangStrings
    language: list[str]
    license: list[str]
    rights_holder: UniqueLang
    rights: LangStrings
    type: str
    format: str
    height: Height | None
    width: Width | None
    depth: Depth | None
    weight: Weight | None
    art_medium: LangStrings
    artform: LangStrings
    is_part_of: list[AnyCreativeWork | BroadcastEvent]
    credit_text: LangStrings
    genre: UniqueLang

    @classmethod
    def from_xml(cls, path: Path) -> Self:
        root = parse_xml_tree(path)
        return cls.from_xml_tree(root)

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        creators = element.findall(schema.creator)
        creators += element.findall(dcterms.creator)
        publishers = element.findall(schema.publisher)
        publishers += element.findall(dcterms.publisher)
        contributors = element.findall(schema.contributor)
        contributors += element.findall(dcterms.contributor)

        is_part_of = [parse_is_part_of(el) for el in element.findall(schema.isPartOf)]

        created = element.find(dcterms.created)
        if created is None:
            raise InvalidXMLError("Missing created element.")

        issued = element.find(dcterms.issued)
        height = element.find(schema.height)
        width = element.find(schema.width)
        depth = element.find(schema.depth)
        weight = element.find(schema.weight)

        return cls(
            __source__=element.__source__,
            identifier=get_text(element, dcterms.identifier),
            title=unique_lang(element, dcterms.title),
            alternative=langstrings(element, dcterms.alternative),
            extent=element.findtext(dcterms.extent),
            available=element.findtext(dcterms.available),
            description=unique_lang(element, dcterms.description),
            abstract=unique_lang(element, dcterms.abstract),
            created=EDTF.from_xml_tree(created),
            issued=EDTF.from_xml_tree(issued) if issued is not None else None,
            spatial=get_text_list(element, dcterms.spatial),
            temporal=langstrings(element, dcterms.temporal),
            subject=langstrings(element, dcterms.subject),
            language=get_text_list(element, dcterms.language),
            license=get_text_list(element, dcterms.license),
            rights_holder=unique_lang(element, dcterms.rightsHolder),
            rights=langstrings(element, dcterms.rights),
            type=get_text(element, dcterms.type),
            format=get_text(element, dcterms.format),
            creator=[Creator.from_xml_tree(el) for el in creators],
            publisher=[Publisher.from_xml_tree(el) for el in publishers],
            contributor=[Contributor.from_xml_tree(el) for el in contributors],
            height=Height.from_xml_tree(height) if height else None,
            width=Width.from_xml_tree(width) if width else None,
            depth=Depth.from_xml_tree(depth) if depth else None,
            weight=Weight.from_xml_tree(weight) if weight else None,
            art_medium=langstrings(element, schema.artMedium),
            artform=langstrings(element, schema.artform),
            is_part_of=is_part_of,
            credit_text=langstrings(element, schema.creditText),
            genre=unique_lang(element, schema.genre),
        )


def get_text(element: _Element, path: str) -> str:
    text = element.findtext(path)
    if text is None:
        raise InvalidXMLError()
    return text


def get_text_list(element: _Element, path: str) -> list[str]:
    return [(el.text if el.text is not None else "") for el in element.findall(path)]
