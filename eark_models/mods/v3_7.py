#            ooo        ooooo   .oooooo.   oooooooooo.    .oooooo..o
#            `88.       .888'  d8P'  `Y8b  `888'   `Y8b  d8P'    `Y8
#             888b     d'888  888      888  888      888 Y88bo.
#             8 Y88. .P  888  888      888  888      888  `"Y8888o.
#             8  `888'   888  888      888  888      888      `"Y88b
#             8    Y     888  `88b    d88'  888     d88' oo     .d8P
#            o8o        o888o  `Y8bood8P'  o888bood8P'   8""88888P'
#
#                   Metadata Object Description Schema.
#                  See http://www.loc.gov/standards/mods/

from typing import Literal, Any, Self, cast, TypedDict, Generator
from pathlib import Path
from enum import Enum
from pydantic.dataclasses import dataclass

from xml.etree.ElementTree import Element
from xml.etree import ElementTree

from eark_models.utils import InvalidXMLError
from eark_models.xlink.v2 import parse_simple_link
import eark_models.namespaces as ns

__all__ = [
    "Mods",
]


class XML(str, Enum):
    lang = "{http://www.w3.org/XML/1998/namespace}lang"


AnyURI = str
AnySimpleType = Any
ID = str

#  _____                     _       _ _      _
# |_   _|   _ _ __   ___  __| |   __| (_) ___| |_
#   | || | | | '_ \ / _ \/ _` |  / _` | |/ __| __|
#   | || |_| | |_) |  __/ (_| | | (_| | | (__| |_
#   |_| \__, | .__/ \___|\__,_|  \__,_|_|\___|\__|
#       |___/|_|
"""
The typed dicts are used as hints for the static type checker.
"""


class LanguageAttributes(TypedDict):
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None


class AuthorityAttributes(TypedDict):
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None


class StringPlusLanguage(TypedDict):
    text: str

    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None


class StringPlusLanguagePlusSupplied(TypedDict):
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Supplied attribute
    supplied: Literal["yes"] | None


class StringPlusLanguagePlusAuthority(TypedDict):
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None


class AltFormatAttributes(TypedDict):
    alt_format: AnyURI | None
    content_type: str | None


def parse_string_plus_language(element: Element) -> StringPlusLanguage:
    if element.text is None:
        raise InvalidXMLError()
    return {
        "text": element.text,
        "lang": element.attrib.get("lang"),
        "xml_lang": element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang"),
        "script": element.attrib.get("script"),
        "transliteration": element.attrib.get("transliteration"),
    }


def parse_language_attributes(element: Element) -> LanguageAttributes:
    return {
        "lang": element.attrib.get("lang"),
        "xml_lang": element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang"),
        "script": element.attrib.get("script"),
        "transliteration": element.attrib.get("transliteration"),
    }


def parse_authority_attributes(element: Element) -> AuthorityAttributes:
    return {
        "authority": element.attrib.get("authority"),
        "authority_uri": element.attrib.get("authorityURI"),
        "value_uri": element.attrib.get("valueURI"),
    }


def parse_string_plus_language_plus_supplied(
    element: Element,
) -> StringPlusLanguagePlusSupplied:
    supplied = element.attrib.get("supplied")
    if supplied is not None and supplied != "yes":
        raise InvalidXMLError()
    return {
        **parse_string_plus_language(element),
        "supplied": supplied,
    }


def parse_string_plus_language_plus_authority(
    element: Element,
) -> StringPlusLanguagePlusAuthority:
    return {
        **parse_string_plus_language(element),
        **parse_authority_attributes(element),
    }


def parse_alt_format_attributes(element: Element) -> AltFormatAttributes:
    return {
        "alt_format": element.attrib.get("altFormat"),
        "content_type": element.attrib.get("contentType"),
    }


#   ____                                        _
#  / ___|___  _ __ ___  _ __ ___   ___  _ __   | |_ _   _ _ __   ___  ___
# | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \  | __| | | | '_ \ / _ \/ __|
# | |__| (_) | | | | | | | | | | | (_) | | | | | |_| |_| | |_) |  __/\__ \
#  \____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|  \__|\__, | .__/ \___||___/
#                                                   |___/|_|

CodeOrText = Literal["code", "text"]


@dataclass(kw_only=True)
class Date:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    encoding: Literal["w3cdtf", "iso8601", "marc", "temper", "edtf"] | None
    qualifier: Literal["approximate", "inferred", "questionable"] | None
    point: Literal["start", "end"] | None
    key_date: Literal["yes"] | None
    calendar: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        encoding = element.attrib.get("encoding")
        if encoding is not None and encoding not in (
            "w3cdtf",
            "iso8601",
            "marc",
            "temper",
            "edtf",
        ):
            raise InvalidXMLError()

        qualifier = element.attrib.get("qualifier")
        if qualifier is not None and qualifier not in (
            "approximate",
            "inferred",
            "questionable",
        ):
            raise InvalidXMLError()

        point = element.attrib.get("point")
        if point is not None and point not in ("start", "end"):
            raise InvalidXMLError()

        key_date = element.attrib.get("key_date")
        if key_date is not None and key_date != "yes":
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language(element),
            encoding=encoding,
            qualifier=qualifier,
            point=point,
            key_date=key_date,
            calendar=element.attrib.get("calendar"),
        )


#  ____       _
# |  _ \ ___ | | ___
# | |_) / _ \| |/ _ \
# |  _ < (_) | |  __/
# |_| \_\___/|_|\___|


@dataclass(kw_only=True)
class RoleTerm:
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Role:
    role_terms: list[RoleTerm]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


#    _    _         _                  _
#   / \  | |__  ___| |_ _ __ __ _  ___| |_
#  / _ \ | '_ \/ __| __| '__/ _` |/ __| __|
# / ___ \| |_) \__ \ |_| | | (_| | (__| |_
# /_/   \_\_.__/|___/\__|_|  \__,_|\___|\__|


@dataclass(kw_only=True)
class Abstract:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    type: str | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    shareable: Literal["no"]
    alt_rep_group: str | None

    # Alternative_format_attributes
    alt_format: AnyURI | None
    content_type: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        shareable = root.attrib.get("shareable")
        if shareable is None:
            shareable = "no"
        if shareable != "no":
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            **parse_simple_link(root),
            shareable=shareable,
            alt_rep_group=root.attrib.get("altRepGroup"),
            **parse_alt_format_attributes(root),
        )


#   ____
#  / ___| ___ _ __  _ __ ___
# | |  _ / _ \ '_ \| '__/ _ \
# | |_| |  __/ | | | | |  __/
#  \____|\___|_| |_|_|  \___|
@dataclass(kw_only=True)
class Genre:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    type: str | None
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        usage = root.attrib.get("usage")

        if usage is not None and usage != "primary":
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language_plus_authority(root),
            type=root.attrib.get("type"),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )


#  ___    _            _   _  __ _
# |_ _|__| | ___ _ __ | |_(_)/ _(_) ___ _ __
#  | |/ _` |/ _ \ '_ \| __| | |_| |/ _ \ '__|
#  | | (_| |  __/ | | | |_| |  _| |  __/ |
# |___\__,_|\___|_| |_|\__|_|_| |_|\___|_|


@dataclass(kw_only=True)
class Identifier:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    type: str | None
    type_uri: str | None
    invalid: Literal["yes"] | None
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        invalid = root.attrib.get("invalid")
        if invalid is not None and invalid != "yes":
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            invalid=invalid,
            alt_rep_group=root.attrib.get("altRepGroup"),
        )


#  _
# | |    __ _ _ __   __ _ _   _  __ _  __ _  ___
# | |   / _` | '_ \ / _` | | | |/ _` |/ _` |/ _ \
# | |__| (_| | | | | (_| | |_| | (_| | (_| |  __/
# |_____\__,_|_| |_|\__, |\__,_|\__,_|\__, |\___|
#                   |___/             |___/


@dataclass(kw_only=True)
class LanguageTerm:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    authority_uri: AnyURI | None
    value_uri: AnyURI | None
    authority: Literal["rfc3066", "iso639-2b", "iso639-3", "rfc4646", "rfc5646"] | None
    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        authority = root.attrib.get("authority")
        if authority is not None and authority not in (
            "rfc3066",
            "iso639-2b",
            "iso639-3",
            "rfc4646",
            "rfc5646",
        ):
            raise InvalidXMLError()

        type = root.attrib.get("type")
        if type is not None and type not in ("code", "text"):
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language(root),
            authority_uri=root.attrib.get("authorityURI"),
            value_uri=root.attrib.get("valueURI"),
            authority=authority,
            type=type,
        )


@dataclass(kw_only=True)
class ScriptTerm:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        type = root.attrib.get("type")
        if type is not None and type not in ("code", "text"):
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language_plus_authority(root),
            type=type,
        )


@dataclass(kw_only=True)
class Language:
    language_term: list[LanguageTerm]
    script_term: list[ScriptTerm]
    object_part: str | None

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        usage = root.attrib.get("usage")
        if usage is not None and usage != "primary":
            raise InvalidXMLError()

        lang_terms = root.iterfind(ns.mods.languageTerm)
        script_terms = root.iterfind(ns.mods.scriptTerm)

        return cls(
            **parse_language_attributes(root),
            language_term=[LanguageTerm.from_xml_tree(el) for el in lang_terms],
            script_term=[ScriptTerm.from_xml_tree(el) for el in script_terms],
            object_part=root.attrib.get("objectPart"),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )


#  _   _
# | \ | | __ _ _ __ ___   ___
# |  \| |/ _` | '_ ` _ \ / _ \
# | |\  | (_| | | | | | |  __/
# |_| \_|\__,_|_| |_| |_|\___|


@dataclass(kw_only=True)
class NamePart:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    type: Literal["date", "family", "given", "termsOfAddress"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class DisplayForm:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Affiliation:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Description:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


# There are two ways to specify the name element
# 1. with `et. al`
# 2. without `et. al`


@dataclass(kw_only=True)
class NameNoEtal:
    options: list[
        NamePart
        # | DisplayForm
        # | Affiliation
        | Role
        # | Description
        # | NameIdentifier
        # | AlternativeName
    ]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class NameEtal:
    # etal: ...
    # options: list[Affiliation | Role | Description]
    pass

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Name:
    content: NameNoEtal | NameEtal
    type: Literal["personal", "corporate", "conference", "family"]
    # display_label: str | None
    # alt_rep_group: str | None
    # name_title_group: str | None
    # usage: Literal["primary"]

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        # TODO
        raise NotImplementedError()


#   ___       _       _         _        __
#  / _ \ _ __(_) __ _(_)_ __   (_)_ __  / _| ___
# | | | | '__| |/ _` | | '_ \  | | '_ \| |_ / _ \
# | |_| | |  | | (_| | | | | | | | | | |  _| (_) |
#  \___/|_|  |_|\__, |_|_| |_| |_|_| |_|_|  \___/
#               |___/


@dataclass(kw_only=True)
class PlaceTerm:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    authority_uri: AnyURI | None
    value_uri: AnyURI | None
    authority: Literal["marcgac", "marccountry", "iso3166"] | None
    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        authority = root.attrib.get("authority")

        if authority is not None and authority not in (
            "marcgac",
            "marccountry",
            "iso3166",
        ):
            raise InvalidXMLError()

        type = root.attrib.get("type")
        if type not in ("code", "text"):
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language(root),
            authority_uri=root.attrib.get("authorityURI"),
            value_uri=root.attrib.get("valueURI"),
            authority=authority,
            type=type,
        )


@dataclass(kw_only=True)
class Place:
    terms: list[PlaceTerm]
    supplied: Literal["yes"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        supplied = root.attrib.get("supplied")
        if supplied is not None and supplied != "yes":
            raise InvalidXMLError()

        return cls(
            terms=[PlaceTerm.from_xml_tree(el) for el in root],
            supplied=supplied,
        )


@dataclass(kw_only=True)
class Publisher:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Supplied attribute
    supplied: Literal["yes"] | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_supplied(root),
            **parse_authority_attributes(root),
        )


@dataclass(kw_only=True)
class DateIssued(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class DateCreated(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class DateCaptured(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class DateValid(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class DateModified(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class CopyrightDate(Date):
    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        return super().from_xml_tree(element)


@dataclass(kw_only=True)
class DateOther:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Edition:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Frequency:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Issuance:
    value: Literal[
        "continuing",
        "monographic",
        "single unit",
        "multipart monograph",
        "serial",
        "integrating resource",
    ]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        text = root.text
        if text is None or text not in (
            "continuing",
            "monographic",
            "single unit",
            "multipart monograph",
            "serial",
            "integrating resource",
        ):
            raise InvalidXMLError()

        return cls(
            value=text,
        )


OriginInfoProperty = (
    Place
    | Publisher
    | DateIssued
    | DateCreated
    | DateCaptured
    | DateValid
    | DateModified
    | CopyrightDate
    | DateOther
    | Edition
    | Issuance
    | Frequency
)


@dataclass(kw_only=True)
class OriginInfo:
    properties: list[OriginInfoProperty]

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # display_label: str | None
    # alt_rep_group: str | None
    event_type: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        properties = [cls._parse_origin_property(el) for el in root]
        return cls(
            properties=properties,
            event_type=root.attrib.get("eventType"),
            **parse_language_attributes(root),
        )

    @classmethod
    def _parse_origin_property(cls, root: Element) -> OriginInfoProperty:
        match root.tag:
            case ns.mods.place:
                return Place.from_xml_tree(root)
            case ns.mods.publisher:
                return Publisher.from_xml_tree(root)
            case ns.mods.dateIssued:
                return DateIssued.from_xml_tree(root)
            case ns.mods.dateCreated:
                return DateCreated.from_xml_tree(root)
            case ns.mods.dateCaptured:
                return DateCaptured.from_xml_tree(root)
            case ns.mods.dateValid:
                return DateValid.from_xml_tree(root)
            case ns.mods.dateModified:
                return DateModified.from_xml_tree(root)
            case ns.mods.copyrightDate:
                return CopyrightDate.from_xml_tree(root)
            case ns.mods.dateOther:
                return DateOther.from_xml_tree(root)
            case ns.mods.edition:
                return Edition.from_xml_tree(root)
            case ns.mods.issuance:
                return Issuance.from_xml_tree(root)
            case ns.mods.frequency:
                return Frequency.from_xml_tree(root)
            case _:
                raise InvalidXMLError()

    @property
    def places(self) -> Generator[Place, None, None]:
        return (cast(Place, p) for p in self.properties if isinstance(p, Place))

    @property
    def publishers(self) -> Generator[Publisher, None, None]:
        return (cast(Publisher, p) for p in self.properties if isinstance(p, Publisher))

    @property
    def dates_issued(self) -> Generator[DateIssued, None, None]:
        return (
            cast(DateIssued, p) for p in self.properties if isinstance(p, DateIssued)
        )

    @property
    def dates_created(self) -> Generator[DateCreated, None, None]:
        return (
            cast(DateCreated, p) for p in self.properties if isinstance(p, DateCreated)
        )

    @property
    def dates_captured(self) -> Generator[DateCaptured, None, None]:
        return (
            cast(DateCaptured, p)
            for p in self.properties
            if isinstance(p, DateCaptured)
        )

    @property
    def dates_valid(self) -> Generator[DateValid, None, None]:
        return (cast(DateValid, p) for p in self.properties if isinstance(p, DateValid))

    @property
    def dates_modified(self) -> Generator[DateModified, None, None]:
        return (
            cast(DateModified, p)
            for p in self.properties
            if isinstance(p, DateModified)
        )

    @property
    def copyright_dates(self) -> Generator[CopyrightDate, None, None]:
        return (
            cast(CopyrightDate, p)
            for p in self.properties
            if isinstance(p, CopyrightDate)
        )

    @property
    def dates_other(self) -> Generator[DateOther, None, None]:
        return (cast(DateOther, p) for p in self.properties if isinstance(p, DateOther))

    @property
    def editions(self) -> Generator[Edition, None, None]:
        return (cast(Edition, p) for p in self.properties if isinstance(p, Edition))

    @property
    def issuances(self) -> Generator[Issuance, None, None]:
        return (cast(Issuance, p) for p in self.properties if isinstance(p, Issuance))

    @property
    def frequencies(self) -> Generator[Frequency, None, None]:
        return (cast(Frequency, p) for p in self.properties if isinstance(p, Frequency))


#  ____  _               _           _
# |  _ \| |__  _   _ ___(_) ___ __ _| |
# | |_) | '_ \| | | / __| |/ __/ _` | |
# |  __/| | | | |_| \__ \ | (_| (_| | |
# |_|   |_| |_|\__, |___/_|\___\__,_|_|
#              |___/
#      _                     _       _   _
#   __| | ___  ___  ___ _ __(_)_ __ | |_(_) ___  _ __
#  / _` |/ _ \/ __|/ __| '__| | '_ \| __| |/ _ \| '_ \
# | (_| |  __/\__ \ (__| |  | | |_) | |_| | (_) | | | |
#  \__,_|\___||___/\___|_|  |_| .__/ \__|_|\___/|_| |_|
#                             |_|


@dataclass(kw_only=True)
class Form:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    type: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_authority(root),
            type=root.attrib.get("type"),
        )


@dataclass(kw_only=True)
class Extent:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Supplied attribute
    supplied: Literal["yes"] | None

    unit: AnySimpleType

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_supplied(root),
            unit=root.attrib.get("unit"),
        )


@dataclass(kw_only=True)
class ReformattingQuality:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class InternetMediaType:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class DigitalOrigin:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class PhysicalDescriptionNote:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    type: str | None
    type_uri: AnyURI | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    id: ID | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            **parse_simple_link(root),
            id=root.attrib.get("ID"),
        )


PhysicalDescriptionProperty = (
    Form
    | ReformattingQuality
    | InternetMediaType
    | Extent
    | DigitalOrigin
    | PhysicalDescriptionNote
)


@dataclass(kw_only=True)
class PhysicalDescription:
    properties: list[PhysicalDescriptionProperty]

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            properties=[
                PhysicalDescription._parse_physical_property(el) for el in root
            ],
            **parse_language_attributes(root),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @classmethod
    def _parse_physical_property(cls, element: Element) -> PhysicalDescriptionProperty:
        match element.tag:
            case ns.mods.form:
                return Form.from_xml_tree(element)
            case ns.mods.reformattingQuality:
                return ReformattingQuality.from_xml_tree(element)
            case ns.mods.internetMediaType:
                return InternetMediaType.from_xml_tree(element)
            case ns.mods.extent:
                return Extent.from_xml_tree(element)
            case ns.mods.digitalOrigin:
                return DigitalOrigin.from_xml_tree(element)
            case ns.mods.note:
                return PhysicalDescriptionNote.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


#  ____      _       _           _   _ _
# |  _ \ ___| | __ _| |_ ___  __| | (_) |_ ___ _ __ ___
# | |_) / _ \ |/ _` | __/ _ \/ _` | | | __/ _ \ '_ ` _ \
# |  _ <  __/ | (_| | ||  __/ (_| | | | ||  __/ | | | | |
# |_| \_\___|_|\__,_|\__\___|\__,_| |_|\__\___|_| |_| |_|


@dataclass(kw_only=True)
class RelatedItem:
    properties: list["ModsProperty"]
    type: (
        Literal[
            "preceding",
            "succeeding",
            "original",
            "host",
            "constituent",
            "series",
            "otherVersion",
            "otherFormat",
            "isReferencedBy",
            "references",
            "reviewOf",
        ]
        | None
    )
    other_type: str | None
    other_type_auth: str | None
    other_type_auth_uri: str | None
    other_type_uri: str | None
    display_label: str | None
    id: ID | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        type = root.attrib.get("type")
        if type is not None and type not in (
            "preceding",
            "succeeding",
            "original",
            "host",
            "constituent",
            "series",
            "otherVersion",
            "otherFormat",
            "isReferencedBy",
            "references",
            "reviewOf",
        ):
            raise InvalidXMLError()

        return cls(
            properties=[Mods._parse_mods_property(el) for el in root],
            type=type,
            other_type=root.attrib.get("otherType"),
            other_type_auth=root.attrib.get("otherTypeAuth"),
            other_type_auth_uri=root.attrib.get("otherTypeAuthURI"),
            other_type_uri=root.attrib.get("otherTypeURI"),
            display_label=root.attrib.get("displayLabel"),
            id=root.attrib.get("ID"),
            **parse_simple_link(root),
        )


#  ____        _     _           _
# / ___| _   _| |__ (_) ___  ___| |_
# \___ \| | | | '_ \| |/ _ \/ __| __|
#  ___) | |_| | |_) | |  __/ (__| |_
# |____/ \__,_|_.__// |\___|\___|\__|
#                 |__/


@dataclass(kw_only=True)
class Topic:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_authority(root),
        )


@dataclass(kw_only=True)
class Geographic:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_authority(root),
        )


@dataclass(kw_only=True)
class Temporal:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class SubjectTitleInfo:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class SubjectName:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class GeographicCode:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class HierarchicalGeographic:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Cartographics:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Occupation:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


SubjectProperty = (
    Topic
    | Geographic
    | Temporal
    | SubjectTitleInfo
    | SubjectName
    | GeographicCode
    | HierarchicalGeographic
    | Cartographics
    | Occupation
    | Genre
)


@dataclass(kw_only=True)
class Subject:
    properties: list[SubjectProperty]
    id: ID | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        usage = root.attrib.get("usage")
        if usage is not None and usage != "primary":
            raise InvalidXMLError()

        return cls(
            properties=[Subject._parse_subject_property(el) for el in root],
            id=root.attrib.get("ID"),
            **parse_authority_attributes(root),
            **parse_language_attributes(root),
            **parse_simple_link(root),
            display_label=root.attrib.get("display_label"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )

    @classmethod
    def _parse_subject_property(cls, element: Element) -> SubjectProperty:
        match element.tag:
            case ns.mods.topic:
                return Topic.from_xml_tree(element)
            case ns.mods.geographic:
                return Geographic.from_xml_tree(element)
            case ns.mods.temporal:
                return Temporal.from_xml_tree(element)
            case ns.mods.titleInfo:
                return SubjectTitleInfo.from_xml_tree(element)
            case ns.mods.name:
                return SubjectName.from_xml_tree(element)
            case ns.mods.geographicCode:
                return GeographicCode.from_xml_tree(element)
            case ns.mods.hierarchicalGeographic:
                return HierarchicalGeographic.from_xml_tree(element)
            case ns.mods.cartographics:
                return Cartographics.from_xml_tree(element)
            case ns.mods.occupation:
                return Occupation.from_xml_tree(element)
            case ns.mods.genre:
                return Genre.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


#  ____                        _   _        __
# |  _ \ ___  ___ ___  _ __ __| | (_)_ __  / _| ___
# | |_) / _ \/ __/ _ \| '__/ _` | | | '_ \| |_ / _ \
# |  _ <  __/ (_| (_) | | | (_| | | | | | |  _| (_) |
# |_| \_\___|\___\___/|_|  \__,_| |_|_| |_|_|  \___/


@dataclass(kw_only=True)
class RecordContentSource:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language_plus_authority(root),
        )


@dataclass(kw_only=True)
class RecordCreationDate:
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


@dataclass(kw_only=True)
class RecordChangeDate:
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


@dataclass(kw_only=True)
class RecordIdentifier:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    source: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
            source=root.attrib.get("source"),
        )


@dataclass(kw_only=True)
class LanguageOfCataloging:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class RecordOrigin:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class DescriptionStandard:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class RecordInfoNote:
    note: "Note"

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(note=Note.from_xml_tree(root))


RecordInfoProperty = (
    RecordContentSource
    | RecordCreationDate
    | RecordChangeDate
    | RecordIdentifier
    | LanguageOfCataloging
    | RecordOrigin
    | DescriptionStandard
    | RecordInfoNote
)


@dataclass(kw_only=True)
class RecordInfo:
    properties: list[RecordInfoProperty]

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            properties=[RecordInfo._parse_record_info_property(el) for el in root],
            **parse_language_attributes(root),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @classmethod
    def _parse_record_info_property(cls, element: Element) -> RecordInfoProperty:
        match element.tag:
            case ns.mods.recordContentSource:
                return RecordContentSource.from_xml_tree(element)
            case ns.mods.recordCreationDate:
                return RecordCreationDate.from_xml_tree(element)
            case ns.mods.recordChangeDate:
                return RecordChangeDate.from_xml_tree(element)
            case ns.mods.recordIdentifier:
                return RecordIdentifier.from_xml_tree(element)
            case ns.mods.languageOfCataloging:
                return LanguageOfCataloging.from_xml_tree(element)
            case ns.mods.recordOrigin:
                return RecordOrigin.from_xml_tree(element)
            case ns.mods.descriptionStandard:
                return DescriptionStandard.from_xml_tree(element)
            case ns.mods.recordInfoNote:
                return RecordInfoNote.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


#   ___  _   _
#  / _ \| |_| |__   ___ _ __
# | | | | __| '_ \ / _ \ '__|
# | |_| | |_| | | |  __/ |
#  \___/ \__|_| |_|\___|_|


@dataclass(kw_only=True)
class AccessCondition:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Classification:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Extension:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Location:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class Part:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class TableOfContents:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


@dataclass(kw_only=True)
class TargetAudience:
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


#  _____                          __
# |_   _|   _ _ __   ___    ___  / _|  _ __ ___  ___  ___  _   _ _ __ ___ ___
#   | || | | | '_ \ / _ \  / _ \| |_  | '__/ _ \/ __|/ _ \| | | | '__/ __/ _ \
#   | || |_| | |_) |  __/ | (_) |  _| | | |  __/\__ \ (_) | |_| | | | (_|  __/
#   |_| \__, | .__/ \___|  \___/|_|   |_|  \___||___/\___/ \__,_|_|  \___\___|
#       |___/|_|


@dataclass(kw_only=True)
class TypeOfResource:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    collection: Literal["yes"] | None
    manuscript: Literal["yes"] | None
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        collection = root.attrib.get("collection")
        if collection is not None and collection != "yes":
            raise InvalidXMLError()

        manuscript = root.attrib.get("manuscript")
        if manuscript is not None and manuscript != "yes":
            raise InvalidXMLError()

        usage = root.attrib.get("usage")
        if usage is not None and usage != "primary":
            raise InvalidXMLError()

        return cls(
            **parse_string_plus_language_plus_authority(root),
            collection=collection,
            manuscript=manuscript,
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )


#  _____ _ _   _        _        __
# |_   _(_) |_| | ___  (_)_ __  / _| ___
#   | | | | __| |/ _ \ | | '_ \| |_ / _ \
#   | | | | |_| |  __/ | | | | |  _| (_) |
#   |_| |_|\__|_|\___| |_|_| |_|_|  \___/


@dataclass(kw_only=True)
class Title:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
        )


@dataclass(kw_only=True)
class SubTitle:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
        )


@dataclass(kw_only=True)
class PartNumber:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
        )


@dataclass(kw_only=True)
class PartName:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
        )


@dataclass(kw_only=True)
class NonSort:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    xml_space: Any

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


TitleInfoProperty = Title | SubTitle | PartNumber | PartName | NonSort


@dataclass(kw_only=True)
class TitleInfo:
    properties: list[TitleInfoProperty]
    type: Literal["abbreviated", "translated", "alternative", "uniform"] | None
    other_type: AnySimpleType | None
    supplied: Literal["yes"] | None
    alt_rep_group: str | None

    # Alternative_format_attributes
    alt_format: AnyURI | None
    content_type: str | None

    name_title_group: str | None
    usage: Literal["primary"] | None
    id: ID | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    # Authority attributes
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        type = root.attrib.get("type")
        if type is not None and type not in (
            "abbreviated",
            "translated",
            "alternative",
            "uniform",
        ):
            raise InvalidXMLError()

        supplied = root.attrib.get("supplied")
        if supplied is not None and supplied != "yes":
            raise InvalidXMLError()

        usage = root.attrib.get("usage")
        if usage is not None and usage != "primary":
            raise InvalidXMLError()

        return cls(
            properties=[cls._parse_title_info_property(el) for el in root],
            type=type,
            other_type=root.attrib.get("other_type"),
            supplied=supplied,
            alt_rep_group=root.attrib.get("alt_rep_group"),
            **parse_alt_format_attributes(root),
            name_title_group=root.attrib.get("nameTitleGroup"),
            usage=usage,
            id=root.attrib.get("id"),
            **parse_authority_attributes(root),
            **parse_simple_link(root),
            **parse_language_attributes(root),
            display_label=root.attrib.get("display_label"),
        )

    @classmethod
    def _parse_title_info_property(cls, root: Element) -> TitleInfoProperty:
        match root.tag:
            case ns.mods.title:
                return Title.from_xml_tree(root)
            case ns.mods.subTitle:
                return SubTitle.from_xml_tree(root)
            case ns.mods.partNumber:
                return PartNumber.from_xml_tree(root)
            case ns.mods.partName:
                return PartName.from_xml_tree(root)
            case ns.mods.nonSort:
                return NonSort.from_xml_tree(root)
            case _:
                raise InvalidXMLError()

    @property
    def titles(self) -> list[Title]:
        return [cast(Title, p) for p in self.properties if isinstance(p, Title)]

    @property
    def subTitles(self) -> list[SubTitle]:
        return [cast(SubTitle, p) for p in self.properties if isinstance(p, SubTitle)]

    @property
    def partNumbers(self) -> list[PartNumber]:
        return [
            cast(PartNumber, p) for p in self.properties if isinstance(p, PartNumber)
        ]

    @property
    def partNames(self) -> list[PartName]:
        return [cast(PartName, p) for p in self.properties if isinstance(p, PartName)]

    @property
    def nonSorts(self) -> list[NonSort]:
        return [cast(NonSort, p) for p in self.properties if isinstance(p, NonSort)]


#  _   _       _
# | \ | | ___ | |_ ___
# |  \| |/ _ \| __/ _ \
# | |\  | (_) | ||  __/
# |_| \_|\___/ \__\___|


@dataclass(kw_only=True)
class Note:
    text: str

    # Language attributes
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    display_label: str | None
    type: str | None
    type_uri: AnyURI | None

    # Simple link attributes
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    id: ID | None
    alt_rep_group: str | None  # missing

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            **parse_string_plus_language(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            **parse_simple_link(root),
            id=root.attrib.get("ID"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )


#  __  __  ___  ____  ____
# |  \/  |/ _ \|  _ \/ ___|
# | |\/| | | | | | | \___ \
# | |  | | |_| | |_| |___) |
# |_|  |_|\___/|____/|____/


ModsProperty = (
    Abstract
    | AccessCondition
    | Classification
    | Extension
    | Genre
    | Identifier
    | Language
    | Location
    | Name
    | Note
    | OriginInfo
    | Part
    | PhysicalDescription
    | RecordInfo
    | RelatedItem
    | Subject
    | TableOfContents
    | TargetAudience
    | TitleInfo
    | TypeOfResource
)

ModsVersions = Literal[
    "3.7",
    "3.6",
    "3.5",
    "3.4",
    "3.3",
    "3.2",
    "3.1",
    "3.0",
]


@dataclass(kw_only=True)
class Mods:
    properties: list[ModsProperty]

    # id: ID | None
    version: ModsVersions | None

    @classmethod
    def from_xml(cls, path: Path) -> Self:
        root = ElementTree.parse(path).getroot()
        return cls.from_xml_tree(root)

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        properties = [cls._parse_mods_property(el) for el in root]
        version = root.attrib.get("version")
        if version is not None and version not in (
            "3.7",
            "3.6",
            "3.5",
            "3.4",
            "3.3",
            "3.2",
            "3.1",
            "3.0",
        ):
            raise InvalidXMLError()

        return cls(
            properties=properties,
            version=version,
        )

    @classmethod
    def _parse_mods_property(cls, element: Element) -> ModsProperty:
        match element.tag:
            case ns.mods.abstract:
                return Abstract.from_xml_tree(element)
            case ns.mods.accessCondition:
                return AccessCondition.from_xml_tree(element)
            case ns.mods.classification:
                return Classification.from_xml_tree(element)
            case ns.mods.extension:
                return Extension.from_xml_tree(element)
            case ns.mods.genre:
                return Genre.from_xml_tree(element)
            case ns.mods.identifier:
                return Identifier.from_xml_tree(element)
            case ns.mods.language:
                return Language.from_xml_tree(element)
            case ns.mods.location:
                return Location.from_xml_tree(element)
            case ns.mods.name:
                return Name.from_xml_tree(element)
            case ns.mods.note:
                return Note.from_xml_tree(element)
            case ns.mods.originInfo:
                return OriginInfo.from_xml_tree(element)
            case ns.mods.part:
                return Part.from_xml_tree(element)
            case ns.mods.physicalDescription:
                return PhysicalDescription.from_xml_tree(element)
            case ns.mods.recordInfo:
                return RecordInfo.from_xml_tree(element)
            case ns.mods.relatedItem:
                return RelatedItem.from_xml_tree(element)
            case ns.mods.subject:
                return Subject.from_xml_tree(element)
            case ns.mods.tableOfContents:
                return TableOfContents.from_xml_tree(element)
            case ns.mods.targetAudience:
                return TargetAudience.from_xml_tree(element)
            case ns.mods.titleInfo:
                return TitleInfo.from_xml_tree(element)
            case ns.mods.typeOfResource:
                return TypeOfResource.from_xml_tree(element)
            case _:
                raise InvalidXMLError()

    @property
    def abstracts(self) -> Generator[Abstract, None, None]:
        return (cast(Abstract, p) for p in self.properties if isinstance(p, Abstract))

    @property
    def access_conditions(self) -> Generator[AccessCondition, None, None]:
        return (
            cast(AccessCondition, p)
            for p in self.properties
            if isinstance(p, AccessCondition)
        )

    @property
    def classifications(self) -> Generator[Classification, None, None]:
        return (
            cast(Classification, p)
            for p in self.properties
            if isinstance(p, Classification)
        )

    @property
    def extensions(self) -> Generator[Extension, None, None]:
        return (cast(Extension, p) for p in self.properties if isinstance(p, Extension))

    @property
    def genres(self) -> Generator[Genre, None, None]:
        return (cast(Genre, p) for p in self.properties if isinstance(p, Genre))

    @property
    def identifiers(self) -> Generator[Identifier, None, None]:
        return (
            cast(Identifier, p) for p in self.properties if isinstance(p, Identifier)
        )

    @property
    def languages(self) -> Generator[Language, None, None]:
        return (cast(Language, p) for p in self.properties if isinstance(p, Language))

    @property
    def locations(self) -> Generator[Location, None, None]:
        return (cast(Location, p) for p in self.properties if isinstance(p, Location))

    @property
    def names(self) -> Generator[Name, None, None]:
        return (cast(Name, p) for p in self.properties if isinstance(p, Name))

    @property
    def notes(self) -> Generator[Note, None, None]:
        return (cast(Note, p) for p in self.properties if isinstance(p, Note))

    @property
    def origin_infos(self) -> Generator[OriginInfo, None, None]:
        return (
            cast(OriginInfo, p) for p in self.properties if isinstance(p, OriginInfo)
        )

    @property
    def parts(self) -> Generator[Part, None, None]:
        return (cast(Part, p) for p in self.properties if isinstance(p, Part))

    @property
    def physical_descriptions(self) -> Generator[PhysicalDescription, None, None]:
        return (
            cast(PhysicalDescription, p)
            for p in self.properties
            if isinstance(p, PhysicalDescription)
        )

    @property
    def record_infos(self) -> Generator[RecordInfo, None, None]:
        return (
            cast(RecordInfo, p) for p in self.properties if isinstance(p, RecordInfo)
        )

    @property
    def related_items(self) -> Generator[RelatedItem, None, None]:
        return (
            cast(RelatedItem, p) for p in self.properties if isinstance(p, RelatedItem)
        )

    @property
    def subjects(self) -> Generator[Subject, None, None]:
        return (cast(Subject, p) for p in self.properties if isinstance(p, Subject))

    @property
    def table_of_contents(self) -> Generator[TableOfContents, None, None]:
        return (
            cast(TableOfContents, p)
            for p in self.properties
            if isinstance(p, TableOfContents)
        )

    @property
    def target_audiences(self) -> Generator[TargetAudience, None, None]:
        return (
            cast(TargetAudience, p)
            for p in self.properties
            if isinstance(p, TargetAudience)
        )

    @property
    def title_infos(self) -> Generator[TitleInfo, None, None]:
        return (cast(TitleInfo, p) for p in self.properties if isinstance(p, TitleInfo))

    @property
    def type_of_resources(self) -> Generator[TypeOfResource, None, None]:
        return (
            cast(TypeOfResource, p)
            for p in self.properties
            if isinstance(p, TypeOfResource)
        )


@dataclass(kw_only=True)
class ModsCollection:
    mods: list[Mods]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()
