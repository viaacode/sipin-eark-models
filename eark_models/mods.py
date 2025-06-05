from typing import Literal, Any, Self, cast

from xml.etree.ElementTree import Element
from xml.etree import ElementTree

from pydantic import BaseModel, Field

from eark_models.utils import InvalidXMLError
from eark_models.xlink import SimpleLink

ns = {
    "mods": "http://www.loc.gov/mods/v3",
    "xlink": "http://www.w3.org/1999/xlink",
}


class ModsMeta(type):
    def __getattr__(self, name: str) -> str:
        return "{http://www.loc.gov/mods/v3}" + name


class _MODS(metaclass=ModsMeta): ...


AnyURI = str
AnySimpleType = Any
ID = str

####### common attributes


class LanguageAttributes(BaseModel):
    lang: str | None
    xml_lang: str | None
    script: str | None
    transliteration: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        return cls(
            lang=root.attrib.get("lang"),
            xml_lang=root.attrib.get("xml:lang"),
            script=root.attrib.get("script"),
            transliteration=root.attrib.get("transliteration"),
        )


class AuthorityAttributes(BaseModel):
    authority: str | None
    authority_uri: AnyURI | None
    value_uri: AnyURI | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            authority=root.attrib.get("authority"),
            authority_uri=root.attrib.get("authorityURI"),
            value_uri=root.attrib.get("valueURI"),
        )


class StringPlusLanguage(BaseModel):
    value: str
    language_attributes: LanguageAttributes

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        text = root.text
        if text is None:
            raise ValueError()
        return cls(
            value=text,
            language_attributes=LanguageAttributes.from_xml_tree(root),
        )


class StringPlusLanguagePlusSupplied(BaseModel):
    string_plus_language: StringPlusLanguage
    supplied: Literal["yes"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        supplied = root.attrib.get("supplied")
        if supplied is None:
            supplied = "yes"
        if supplied != "yes":
            raise ValueError()
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            supplied=supplied,
        )


class StringPlusLanguagePlusAuthority(BaseModel):
    string_plus_language: StringPlusLanguage
    authority_attributes: AuthorityAttributes

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            authority_attributes=AuthorityAttributes.from_xml_tree(root),
        )


class AltFormatAttributes(BaseModel):
    alt_format: AnyURI | None
    content_type: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            alt_format=root.attrib.get("altFormat"),
            content_type=root.attrib.get("contentType"),
        )


###### Common types

CodeOrText = Literal["code", "text"]


class Date(BaseModel):
    string_plus_language: StringPlusLanguage
    encoding: Literal["w3cdtf", "iso8601", "marc", "temper", "edtf"] | None
    qualifier: Literal["approximate", "inferred", "questionable"] | None
    point: Literal["start", "end"] | None
    key_date: Literal["yes"]
    calendar: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        encoding = root.attrib.get("encoding")
        if encoding is not None and encoding not in (
            "w3cdtf",
            "iso8601",
            "marc",
            "temper",
            "edtf",
        ):
            raise ValueError()

        qualifier = root.attrib.get("qualifier")
        if qualifier is not None and qualifier not in (
            "approximate",
            "inferred",
            "questionable",
        ):
            raise ValueError()

        point = root.attrib.get("point")
        if point is not None and point not in ("start", "end"):
            raise ValueError()

        key_date = root.attrib.get("key_date")
        if key_date is None:
            key_date = "yes"
        if key_date != "yes":
            raise ValueError()

        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            encoding=encoding,
            qualifier=qualifier,
            point=point,
            key_date=key_date,
            calendar=root.attrib.get("calendar"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


######## Role


class RoleTerm(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class Role(BaseModel):
    role_terms: list[RoleTerm] = Field(min_length=1)

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


########## Top level: Abstract


class Abstract(BaseModel):
    string_plus_language: StringPlusLanguage
    display_label: str | None
    type: str | None
    simple_link: SimpleLink | None
    shareable: Literal["no"]
    alt_rep_group: str | None
    alt_format_attributes: AltFormatAttributes

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        shareable = root.attrib.get("shareable")
        if shareable is None:
            shareable = "no"
        if shareable != "no":
            raise ValueError()

        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            simple_link=SimpleLink.from_xml_tree(root),
            shareable=shareable,
            alt_rep_group=root.attrib.get("altRepGroup"),
            alt_format_attributes=AltFormatAttributes.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


########## Top level: Genre


class Genre(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    type: str | None
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        usage = root.attrib.get("usage")
        if usage is None:
            usage = "primary"

        if usage != "primary":
            raise ValueError()

        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
            type=root.attrib.get("type"),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


########## Top level: Identifier


class Identifier(BaseModel):
    string_plus_language: StringPlusLanguage
    display_label: str | None
    type: str | None
    type_uri: str | None
    invalid: Literal["yes"]
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        invalid = root.attrib.get("invalid")
        if invalid is None:
            invalid = "yes"

        if invalid != "yes":
            raise ValueError()

        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            invalid=invalid,
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


########################
#       Top level: Language       #
# ######################


class LanguageTerm(BaseModel):
    string_plus_language: StringPlusLanguage
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
            raise ValueError()

        type = root.attrib.get("type")
        if type is not None and type not in ("code", "text"):
            raise ValueError()

        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            authority_uri=root.attrib.get("authorityURI"),
            value_uri=root.attrib.get("valueURI"),
            authority=authority,
            type=type,
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class ScriptTerm(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    type: CodeOrText | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        type = root.attrib.get("type")
        if type is not None and type not in ("code", "text"):
            raise ValueError()

        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
            type=type,
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class Language(BaseModel):
    language_term: list[LanguageTerm] = Field(min_length=1)
    script_term: list[ScriptTerm]
    object_part: str | None
    language_attributes: LanguageAttributes
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        usage = root.attrib.get("usage")
        if usage is None:
            usage = "primary"
        if usage != "primary":
            raise ValueError()

        lang_terms = root.iterfind(_MODS.languageTerm)
        script_terms = root.iterfind(_MODS.scriptTerm)

        return cls(
            language_term=[LanguageTerm.from_xml_tree(el) for el in lang_terms],
            script_term=[ScriptTerm.from_xml_tree(el) for el in script_terms],
            object_part=root.attrib.get("objectPart"),
            language_attributes=LanguageAttributes.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )


########################
#         Top level: Name         #
# ######################


class NamePart(BaseModel):
    string_plus_language: StringPlusLanguage
    type: Literal["date", "family", "given", "termsOfAddress"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class DisplayForm(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class Affiliation(BaseModel):

    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class Description(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()

    @property
    def value(self) -> str:
        return self.string_plus_language.value


# There are two ways to specify the name element
# 1. with `et. al`
# 2. without `et. al`


class NameNoEtal(BaseModel):
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


class NameEtal(BaseModel):
    # etal: ...
    # options: list[Affiliation | Role | Description]
    pass

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Name(BaseModel):
    content: NameNoEtal | NameEtal
    type: Literal["personal", "corporate", "conference", "family"]
    # display_label: str | None
    # alt_rep_group: str | None
    # name_title_group: str | None
    # usage: Literal["primary"]

    language_attributes: LanguageAttributes
    authority_attributes: AuthorityAttributes
    simple_link: SimpleLink

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        # TODO
        raise NotImplementedError()


#### Top level: Origin info


class PlaceTerm(BaseModel):
    string_plus_language: StringPlusLanguage
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
            raise ValueError()

        type = root.attrib.get("type")
        if type not in ("code", "text"):
            raise ValueError()

        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            authority_uri=root.attrib.get("authorityURI"),
            value_uri=root.attrib.get("valueURI"),
            authority=authority,
            type=type,
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class Place(BaseModel):
    terms: list[PlaceTerm] = Field(min_length=1)
    supplied: Literal["yes"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        supplied = root.attrib.get("supplied")
        if supplied is None:
            supplied = "yes"
        if supplied != "yes":
            raise ValueError()

        return cls(
            terms=[PlaceTerm.from_xml_tree(el) for el in root],
            supplied=supplied,
        )


class Publisher(BaseModel):
    string_plus_language_plus_supplied: StringPlusLanguagePlusSupplied
    authority_attributes: AuthorityAttributes

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_supplied=StringPlusLanguagePlusSupplied.from_xml_tree(
                root
            ),
            authority_attributes=AuthorityAttributes.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_supplied.string_plus_language.value


class DateIssued(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class DateCreated(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class DateCaptured(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class DateValid(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class DateModified(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class CopyrightDate(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class DateOther(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Edition(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Frequency(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Issuance(BaseModel):
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
            raise ValueError()

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


class OriginInfo(BaseModel):
    properties: list[OriginInfoProperty] = Field(min_length=1)
    language_attributes: LanguageAttributes
    # display_label: str | None
    # alt_rep_group: str | None
    eventType: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        properties = [cls._parse_origin_property(el) for el in root]
        return cls(
            properties=properties,
            eventType=root.attrib.get("eventType"),
            language_attributes=LanguageAttributes.from_xml_tree(root),
        )

    @classmethod
    def _parse_origin_property(cls, root: Element) -> OriginInfoProperty:
        match root.tag:
            case _MODS.place:
                return Place.from_xml_tree(root)
            case _MODS.publisher:
                return Publisher.from_xml_tree(root)
            case _MODS.dateIssued:
                return DateIssued.from_xml_tree(root)
            case _MODS.dateCreated:
                return DateCreated.from_xml_tree(root)
            case _MODS.dateCaptured:
                return DateCaptured.from_xml_tree(root)
            case _MODS.dateValid:
                return DateValid.from_xml_tree(root)
            case _MODS.dateModified:
                return DateModified.from_xml_tree(root)
            case _MODS.copyrightDate:
                return CopyrightDate.from_xml_tree(root)
            case _MODS.dateOther:
                return DateOther.from_xml_tree(root)
            case _MODS.edition:
                return Edition.from_xml_tree(root)
            case _MODS.issuance:
                return Issuance.from_xml_tree(root)
            case _MODS.frequency:
                return Frequency.from_xml_tree(root)
            case _:
                raise InvalidXMLError()

    @property
    def places(self) -> list[Place]:
        return [cast(Place, p) for p in self.properties if isinstance(p, Place)]

    @property
    def publishers(self) -> list[Publisher]:
        return [cast(Publisher, p) for p in self.properties if isinstance(p, Publisher)]

    @property
    def datesIssued(self) -> list[DateIssued]:
        return [
            cast(DateIssued, p) for p in self.properties if isinstance(p, DateIssued)
        ]

    @property
    def datesCreated(self) -> list[DateCreated]:
        return [
            cast(DateCreated, p) for p in self.properties if isinstance(p, DateCreated)
        ]

    @property
    def datesCaptured(self) -> list[DateCaptured]:
        return [
            cast(DateCaptured, p)
            for p in self.properties
            if isinstance(p, DateCaptured)
        ]

    @property
    def datesValid(self) -> list[DateValid]:
        return [cast(DateValid, p) for p in self.properties if isinstance(p, DateValid)]

    @property
    def datesModified(self) -> list[DateModified]:
        return [
            cast(DateModified, p)
            for p in self.properties
            if isinstance(p, DateModified)
        ]

    @property
    def copyrightDates(self) -> list[CopyrightDate]:
        return [
            cast(CopyrightDate, p)
            for p in self.properties
            if isinstance(p, CopyrightDate)
        ]

    @property
    def datesOther(self) -> list[DateOther]:
        return [cast(DateOther, p) for p in self.properties if isinstance(p, DateOther)]

    @property
    def editions(self) -> list[Edition]:
        return [cast(Edition, p) for p in self.properties if isinstance(p, Edition)]

    @property
    def issuances(self) -> list[Issuance]:
        return [cast(Issuance, p) for p in self.properties if isinstance(p, Issuance)]

    @property
    def frequencies(self) -> list[Frequency]:
        return [cast(Frequency, p) for p in self.properties if isinstance(p, Frequency)]


####### Top level: Physical description


class Form(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    type: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
            type=root.attrib.get("type"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class Extent(BaseModel):
    string_plus_language_plus_supplied: StringPlusLanguagePlusSupplied
    unit: AnySimpleType

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_supplied=StringPlusLanguagePlusSupplied.from_xml_tree(
                root
            ),
            unit=root.attrib.get("unit"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_supplied.string_plus_language.value


class ReformattingQuality(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class InternetMediaType(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class DigitalOrigin(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class PhysicalDescriptionNote(BaseModel):
    string_plus_language: StringPlusLanguage
    display_label: str | None
    type: str | None
    type_uri: AnyURI | None
    simple_link: SimpleLink
    id: ID | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            simple_link=SimpleLink.from_xml_tree(root),
            id=root.attrib.get("ID"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


PhysicalDescriptionProperty = (
    Form
    | ReformattingQuality
    | InternetMediaType
    | Extent
    | DigitalOrigin
    | PhysicalDescriptionNote
)


class PhysicalDescription(BaseModel):
    properties: list[PhysicalDescriptionProperty] = Field(min_length=1)
    language_attributes: LanguageAttributes
    display_label: str | None
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            properties=[
                PhysicalDescription._parse_physical_property(el) for el in root
            ],
            language_attributes=LanguageAttributes.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @classmethod
    def _parse_physical_property(cls, element: Element) -> PhysicalDescriptionProperty:
        match element.tag:
            case _MODS.form:
                return Form.from_xml_tree(element)
            case _MODS.reformattingQuality:
                return ReformattingQuality.from_xml_tree(element)
            case _MODS.internetMediaType:
                return InternetMediaType.from_xml_tree(element)
            case _MODS.extent:
                return Extent.from_xml_tree(element)
            case _MODS.digitalOrigin:
                return DigitalOrigin.from_xml_tree(element)
            case _MODS.note:
                return PhysicalDescriptionNote.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


##### Top level: Related item


class RelatedItem(BaseModel):
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

    simple_link: SimpleLink

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
            raise ValueError()

        return cls(
            properties=[MODS._parse_mods_property(el) for el in root],
            type=type,
            other_type=root.attrib.get("otherType"),
            other_type_auth=root.attrib.get("otherTypeAuth"),
            other_type_auth_uri=root.attrib.get("otherTypeAuthURI"),
            other_type_uri=root.attrib.get("otherTypeURI"),
            display_label=root.attrib.get("displayLabel"),
            id=root.attrib.get("ID"),
            simple_link=SimpleLink.from_xml_tree(root),
        )


#### Top level: Subject
class Topic(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class Geographic(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class Temporal(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class SubjectTitleInfo(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class SubjectName(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class GeographicCode(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class HierarchicalGeographic(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Cartographics(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Occupation(BaseModel):
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


class Subject(BaseModel):
    properties: list[SubjectProperty]
    id: ID | None
    authority_attributes: AuthorityAttributes
    language_attributes: LanguageAttributes
    simple_link: SimpleLink
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        usage = root.attrib.get("usage")
        if usage is None:
            usage = "primary"
        if usage != "primary":
            raise ValueError()

        return cls(
            properties=[Subject._parse_subject_property(el) for el in root],
            id=root.attrib.get("ID"),
            authority_attributes=AuthorityAttributes.from_xml_tree(root),
            language_attributes=LanguageAttributes.from_xml_tree(root),
            simple_link=SimpleLink.from_xml_tree(root),
            display_label=root.attrib.get("display_label"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )

    @classmethod
    def _parse_subject_property(cls, element: Element) -> SubjectProperty:
        match element.tag:
            case _MODS.topic:
                return Topic.from_xml_tree(element)
            case _MODS.geographic:
                return Geographic.from_xml_tree(element)
            case _MODS.temporal:
                return Temporal.from_xml_tree(element)
            case _MODS.titleInfo:
                return SubjectTitleInfo.from_xml_tree(element)
            case _MODS.name:
                return SubjectName.from_xml_tree(element)
            case _MODS.geographicCode:
                return GeographicCode.from_xml_tree(element)
            case _MODS.hierarchicalGeographic:
                return HierarchicalGeographic.from_xml_tree(element)
            case _MODS.cartographics:
                return Cartographics.from_xml_tree(element)
            case _MODS.occupation:
                return Occupation.from_xml_tree(element)
            case _MODS.genre:
                return Genre.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


### Top level: RecordInfo


class RecordContentSource(BaseModel):
    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


class RecordCreationDate(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class RecordChangeDate(BaseModel):
    date: Date

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            date=Date.from_xml_tree(root),
        )


class RecordIdentifier(BaseModel):
    string_plus_language: StringPlusLanguage
    source: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            source=root.attrib.get("source"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class LanguageOfCataloging(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class RecordOrigin(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class DescriptionStandard(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class RecordInfoNote(BaseModel):
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


class RecordInfo(BaseModel):
    properties: list[RecordInfoProperty] = Field(min_length=1)
    language_attributes: LanguageAttributes
    display_label: str | None
    alt_rep_group: str | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            properties=[RecordInfo._parse_record_info_property(el) for el in root],
            language_attributes=LanguageAttributes.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @classmethod
    def _parse_record_info_property(cls, element: Element) -> RecordInfoProperty:
        match element.tag:
            case _MODS.recordContentSource:
                return RecordContentSource.from_xml_tree(element)
            case _MODS.recordCreationDate:
                return RecordCreationDate.from_xml_tree(element)
            case _MODS.recordChangeDate:
                return RecordChangeDate.from_xml_tree(element)
            case _MODS.recordIdentifier:
                return RecordIdentifier.from_xml_tree(element)
            case _MODS.languageOfCataloging:
                return LanguageOfCataloging.from_xml_tree(element)
            case _MODS.recordOrigin:
                return RecordOrigin.from_xml_tree(element)
            case _MODS.descriptionStandard:
                return DescriptionStandard.from_xml_tree(element)
            case _MODS.recordInfoNote:
                return RecordInfoNote.from_xml_tree(element)
            case _:
                raise InvalidXMLError()


##### Other top level elements


class AccessCondition(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Classification(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Extension(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Location(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class Part(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class TableOfContents(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


class TargetAudience(BaseModel):
    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()


######## Top level: type of resource


class TypeOfResource(BaseModel):

    string_plus_language_plus_authority: StringPlusLanguagePlusAuthority
    collection: Literal["yes"]
    manuscript: Literal["yes"]
    display_label: str | None
    alt_rep_group: str | None
    usage: Literal["primary"]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        collection = root.attrib.get("collection")
        if collection is None:
            collection = "yes"
        if collection != "yes":
            raise ValueError()

        manuscript = root.attrib.get("manuscript")
        if manuscript is None:
            manuscript = "yes"
        if manuscript != "yes":
            raise ValueError()

        usage = root.attrib.get("usage")
        if usage is None:
            usage = "primary"
        if usage != "primary":
            raise ValueError()

        return cls(
            string_plus_language_plus_authority=StringPlusLanguagePlusAuthority.from_xml_tree(
                root
            ),
            collection=collection,
            manuscript=manuscript,
            display_label=root.attrib.get("displayLabel"),
            alt_rep_group=root.attrib.get("altRepGroup"),
            usage=usage,
        )

    @property
    def value(self) -> str:
        return self.string_plus_language_plus_authority.string_plus_language.value


########## Top level: Title Info


class Title(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class SubTitle(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class PartNumber(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class PartName(BaseModel):
    string_plus_language: StringPlusLanguage

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


class NonSort(BaseModel):
    string_plus_language: StringPlusLanguage
    xml_space: Any

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()

    @property
    def value(self) -> str:
        return self.string_plus_language.value


TitleInfoProperty = Title | SubTitle | PartNumber | PartName | NonSort


class TitleInfo(BaseModel):
    properties: list[TitleInfoProperty]
    type: Literal["abbreviated", "translated", "alternative", "uniform"] | None
    other_type: AnySimpleType | None
    supplied: Literal["yes"]
    alt_rep_group: str | None
    alt_format_attributes: AltFormatAttributes
    nameTitleGroup: str | None
    usage: Literal["primary"]
    id: ID | None
    authority_attributes: AuthorityAttributes
    simple_link: SimpleLink
    language_attributes: LanguageAttributes
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
            raise ValueError()

        supplied = root.attrib.get("supplied")
        if supplied is None:
            supplied = "yes"
        if supplied != "yes":
            raise ValueError()

        usage = root.attrib.get("usage")
        if usage is None:
            usage = "primary"
        if usage != "primary":
            raise ValueError()

        return cls(
            properties=[cls._parse_title_info_property(el) for el in root],
            type=type,
            other_type=root.attrib.get("other_type"),
            supplied=supplied,
            alt_rep_group=root.attrib.get("alt_rep_group"),
            alt_format_attributes=AltFormatAttributes.from_xml_tree(root),
            nameTitleGroup=root.attrib.get("nameTitleGroup"),
            usage=usage,
            id=root.attrib.get("id"),
            authority_attributes=AuthorityAttributes.from_xml_tree(root),
            simple_link=SimpleLink.from_xml_tree(root),
            language_attributes=LanguageAttributes.from_xml_tree(root),
            display_label=root.attrib.get("display_label"),
        )

    @classmethod
    def _parse_title_info_property(cls, root: Element) -> TitleInfoProperty:
        match root.tag:
            case _MODS.title:
                return Title.from_xml_tree(root)
            case _MODS.subTitle:
                return SubTitle.from_xml_tree(root)
            case _MODS.partNumber:
                return PartNumber.from_xml_tree(root)
            case _MODS.partName:
                return PartName.from_xml_tree(root)
            case _MODS.nonSort:
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


##### Top level: Note


class Note(BaseModel):
    string_plus_language: StringPlusLanguage
    display_label: str | None
    type: str | None
    type_uri: AnyURI | None
    simple_link: SimpleLink
    id: ID | None
    alt_rep_group: str | None  # missing

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        return cls(
            string_plus_language=StringPlusLanguage.from_xml_tree(root),
            display_label=root.attrib.get("displayLabel"),
            type=root.attrib.get("type"),
            type_uri=root.attrib.get("typeURI"),
            simple_link=SimpleLink.from_xml_tree(root),
            id=root.attrib.get("ID"),
            alt_rep_group=root.attrib.get("altRepGroup"),
        )

    @property
    def value(self) -> str:
        return self.string_plus_language.value


#### Top level: MODS


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


class MODS(BaseModel):
    properties: list[ModsProperty]

    # id: ID | None
    version: ModsVersions | None

    @classmethod
    def from_xml(cls, path: str) -> Self:
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
            raise ValueError()

        return cls(
            properties=properties,
            version=version,
        )

    @classmethod
    def _parse_mods_property(cls, element: Element) -> ModsProperty:
        match element.tag:
            case _MODS.abstract:
                return Abstract.from_xml_tree(element)
            case _MODS.accessCondition:
                return AccessCondition.from_xml_tree(element)
            case _MODS.classification:
                return Classification.from_xml_tree(element)
            case _MODS.extension:
                return Extension.from_xml_tree(element)
            case _MODS.genre:
                return Genre.from_xml_tree(element)
            case _MODS.identifier:
                return Identifier.from_xml_tree(element)
            case _MODS.language:
                return Language.from_xml_tree(element)
            case _MODS.location:
                return Location.from_xml_tree(element)
            case _MODS.name:
                return Name.from_xml_tree(element)
            case _MODS.note:
                return Note.from_xml_tree(element)
            case _MODS.originInfo:
                return OriginInfo.from_xml_tree(element)
            case _MODS.part:
                return Part.from_xml_tree(element)
            case _MODS.physicalDescription:
                return PhysicalDescription.from_xml_tree(element)
            case _MODS.recordInfo:
                return RecordInfo.from_xml_tree(element)
            case _MODS.relatedItem:
                return RelatedItem.from_xml_tree(element)
            case _MODS.subject:
                return Subject.from_xml_tree(element)
            case _MODS.tableOfContents:
                return TableOfContents.from_xml_tree(element)
            case _MODS.targetAudience:
                return TargetAudience.from_xml_tree(element)
            case _MODS.titleInfo:
                return TitleInfo.from_xml_tree(element)
            case _MODS.typeOfResource:
                return TypeOfResource.from_xml_tree(element)
            case _:
                raise InvalidXMLError()

    @property
    def abstracts(self) -> list[Abstract]:
        return [cast(Abstract, p) for p in self.properties if isinstance(p, Abstract)]

    @property
    def accessConditions(self) -> list[AccessCondition]:
        return [
            cast(AccessCondition, p)
            for p in self.properties
            if isinstance(p, AccessCondition)
        ]

    @property
    def classifications(self) -> list[Classification]:
        return [
            cast(Classification, p)
            for p in self.properties
            if isinstance(p, Classification)
        ]

    @property
    def extensions(self) -> list[Extension]:
        return [cast(Extension, p) for p in self.properties if isinstance(p, Extension)]

    @property
    def genres(self) -> list[Genre]:
        return [cast(Genre, p) for p in self.properties if isinstance(p, Genre)]

    @property
    def identifiers(self) -> list[Identifier]:
        return [
            cast(Identifier, p) for p in self.properties if isinstance(p, Identifier)
        ]

    @property
    def languages(self) -> list[Language]:
        return [cast(Language, p) for p in self.properties if isinstance(p, Language)]

    @property
    def locations(self) -> list[Location]:
        return [cast(Location, p) for p in self.properties if isinstance(p, Location)]

    @property
    def names(self) -> list[Name]:
        return [cast(Name, p) for p in self.properties if isinstance(p, Name)]

    @property
    def notes(self) -> list[Note]:
        return [cast(Note, p) for p in self.properties if isinstance(p, Note)]

    @property
    def originInfos(self) -> list[OriginInfo]:
        return [
            cast(OriginInfo, p) for p in self.properties if isinstance(p, OriginInfo)
        ]

    @property
    def parts(self) -> list[Part]:
        return [cast(Part, p) for p in self.properties if isinstance(p, Part)]

    @property
    def physicalDescriptions(self) -> list[PhysicalDescription]:
        return [
            cast(PhysicalDescription, p)
            for p in self.properties
            if isinstance(p, PhysicalDescription)
        ]

    @property
    def recordInfos(self) -> list[RecordInfo]:
        return [
            cast(RecordInfo, p) for p in self.properties if isinstance(p, RecordInfo)
        ]

    @property
    def relatedItems(self) -> list[RelatedItem]:
        return [
            cast(RelatedItem, p) for p in self.properties if isinstance(p, RelatedItem)
        ]

    @property
    def subjects(self) -> list[Subject]:
        return [cast(Subject, p) for p in self.properties if isinstance(p, Subject)]

    @property
    def tableOfContentss(self) -> list[TableOfContents]:
        return [
            cast(TableOfContents, p)
            for p in self.properties
            if isinstance(p, TableOfContents)
        ]

    @property
    def targetAudiences(self) -> list[TargetAudience]:
        return [
            cast(TargetAudience, p)
            for p in self.properties
            if isinstance(p, TargetAudience)
        ]

    @property
    def titleInfos(self) -> list[TitleInfo]:
        return [cast(TitleInfo, p) for p in self.properties if isinstance(p, TitleInfo)]

    @property
    def typeOfResources(self) -> list[TypeOfResource]:
        return [
            cast(TypeOfResource, p)
            for p in self.properties
            if isinstance(p, TypeOfResource)
        ]


class MODSCollection(BaseModel):
    mods: list[MODS]

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:
        raise NotImplementedError()
