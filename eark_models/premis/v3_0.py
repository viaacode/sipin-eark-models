from typing import Literal, Self
from pathlib import Path
from itertools import chain
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

ns = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "premis": "http://www.loc.gov/premis/v3",
}


class PremisMeta(type):
    def __getattr__(self, name: str) -> str:
        return "{http://www.loc.gov/premis/v3}" + name


class _Premis(metaclass=PremisMeta): ...


@dataclass(kw_only=True)
class StringPlusAuthority:
    text: str
    authority: str | None
    authority_uri: str | None
    value_uri: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            raise ValueError()

        return cls(
            text=element.text,
            authority=element.get("authority"),
            authority_uri=element.get("authorityURI"),
            value_uri=element.get("valueURI"),
        )


########## Object ##########


@dataclass(kw_only=True)
class ObjectIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class ObjectIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class ObjectIdentifier:
    type: ObjectIdentifierType
    value: ObjectIdentifierValue
    simple_link: str | None

    @property
    def is_uuid(self):
        return self.type.text == "UUID"

    @property
    def is_pid(self):
        return self.type.text == "MEEMOO-PID"

    @property
    def is_primary_identifier(self):
        return self.type.text == "MEEMOO-LOCAL-ID"

    @property
    def is_local_identifier(self):
        return (
            self.type.text != "UUID"
            and self.type.text != "MEEMOO-PID"
            and self.type.text != "MEEMOO-LOCAL-ID"
        )

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type = element.find(_Premis.objectIdentifierType)
        if type is None:
            raise ValueError()
        value = element.find(_Premis.objectIdentifierValue)
        if value is None:
            raise ValueError()

        return cls(
            type=ObjectIdentifierType.from_xml_tree(type),
            value=ObjectIdentifierValue.from_xml_tree(value),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class MessageDigestAlgorithm(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class MessageDigest:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class Fixity:
    message_digest_algorithm: MessageDigestAlgorithm
    message_digest: MessageDigest
    message_digest_originator: StringPlusAuthority | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        algo_elem = element.find(_Premis.messageDigestAlgorithm)
        if algo_elem is None:
            raise ValueError("Missing messageDigestAlgorithm")
        digest_elem = element.find(_Premis.messageDigest)
        if digest_elem is None:
            raise ValueError("Missing messageDigest")
        originator_elem = element.find(_Premis.messageDigestOriginator)

        return cls(
            message_digest_algorithm=MessageDigestAlgorithm.from_xml_tree(algo_elem),
            message_digest=MessageDigest.from_xml_tree(digest_elem),
            message_digest_originator=(
                StringPlusAuthority.from_xml_tree(originator_elem)
                if originator_elem is not None
                else None
            ),
        )


@dataclass(kw_only=True)
class FormatName(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class FormatRegistryName(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class FormatRegistryKey(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class FormatRegistryRole(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class FormatVersion:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class FormatDesignation:
    name: FormatName
    version: FormatVersion | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        name_elem = element.find(_Premis.formatName)
        if name_elem is None:
            raise ValueError("Missing formatName")
        version_elem = element.find(_Premis.formatVersion)
        return cls(
            name=FormatName.from_xml_tree(name_elem),
            version=(
                FormatVersion.from_xml_tree(version_elem)
                if version_elem is not None
                else None
            ),
        )


@dataclass(kw_only=True)
class FormatRegistry:
    name: FormatRegistryName
    key: FormatRegistryKey
    role: FormatRegistryRole | None
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        name_elem = element.find(_Premis.formatRegistryName)
        if name_elem is None:
            raise ValueError("Missing formatRegistryName")
        key_elem = element.find(_Premis.formatRegistryKey)
        if key_elem is None:
            raise ValueError("Missing formatRegistryKey")
        role_elem = element.find(_Premis.formatRegistryRole)
        return cls(
            name=FormatRegistryName.from_xml_tree(name_elem),
            key=FormatRegistryKey.from_xml_tree(key_elem),
            role=(
                FormatRegistryRole.from_xml_tree(role_elem)
                if role_elem is not None
                else None
            ),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class FormatNote:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class Format:
    designation: FormatDesignation | None
    registry: FormatRegistry | None
    note: list[FormatNote]

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        designation_elem = element.find(_Premis.formatDesignation)
        registry_elem = element.find(_Premis.formatRegistry)
        notes = [
            FormatNote.from_xml_tree(note_elem)
            for note_elem in element.findall(_Premis.formatNote)
        ]
        return cls(
            designation=(
                FormatDesignation.from_xml_tree(designation_elem)
                if designation_elem is not None
                else None
            ),
            registry=(
                FormatRegistry.from_xml_tree(registry_elem)
                if registry_elem is not None
                else None
            ),
            note=notes,
        )


@dataclass(kw_only=True)
class Size:
    value: int

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            raise ValueError("Size element has no text")
        return cls(value=int(element.text))


@dataclass(kw_only=True)
class ObjectCharacteristics:
    fixity: list[Fixity]
    size: Size | None
    format: list[Format]
    # creating_application: ...
    # inhibitors: ...
    # object_characteristics_extension: ...

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        fixities = [
            Fixity.from_xml_tree(fix_elem)
            for fix_elem in element.findall(_Premis.fixity)
        ]
        size_elem = element.find(_Premis.size)
        formats = [
            Format.from_xml_tree(fmt_elem)
            for fmt_elem in element.findall(_Premis.format)
        ]
        return cls(
            fixity=fixities,
            size=Size.from_xml_tree(size_elem) if size_elem is not None else None,
            format=formats,
        )


@dataclass(kw_only=True)
class OriginalName:
    text: str
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="", simple_link=element.get("simpleLink"))
        return cls(
            text=element.text,
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class RelatedObjectIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class RelatedObjectIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class RelatedObjectIdentifier:
    type: RelatedObjectIdentifierType
    value: RelatedObjectIdentifierValue
    # sequence: ... | None
    # RelObjectXmlID
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.relatedObjectIdentifierType)
        if type_elem is None:
            raise ValueError("Missing relatedObjectIdentifierType")
        value_elem = element.find(_Premis.relatedObjectIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing relatedObjectIdentifierValue")
        return cls(
            type=RelatedObjectIdentifierType.from_xml_tree(type_elem),
            value=RelatedObjectIdentifierValue.from_xml_tree(value_elem),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class RelationshipType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class RelationshipSubType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class Relationship:
    type: RelationshipType
    sub_type: RelationshipSubType
    related_object_identifier: list[RelatedObjectIdentifier]
    # related_event_identifier: list[...] = element(default_factory=list)
    # related_environment_purpose: list[...] = element(default_factory=list)
    # related_environment_characteristic: list[...] | None = element(default=None)

    @property
    def related_object_uuid(self) -> str:
        return next(
            (
                id.value.text
                for id in self.related_object_identifier
                if id.type.text == "UUID"
            )
        )

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.relationshipType)
        if type_elem is None:
            raise ValueError("Missing relationshipType")
        sub_type_elem = element.find(_Premis.relationshipSubType)
        if sub_type_elem is None:
            raise ValueError("Missing relationshipSubType")
        related_obj_elems = element.findall(_Premis.relatedObjectIdentifier)
        related_object_identifier = [
            RelatedObjectIdentifier.from_xml_tree(e) for e in related_obj_elems
        ]
        return cls(
            type=RelationshipType.from_xml_tree(type_elem),
            sub_type=RelationshipSubType.from_xml_tree(sub_type_elem),
            related_object_identifier=related_object_identifier,
        )


@dataclass(kw_only=True)
class SignificantPropertiesType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class SignificantPropertiesValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class SignificantProperties:
    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    type: SignificantPropertiesType | None
    value: SignificantPropertiesValue | None
    extension: list[Element]

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.significantPropertiesType)
        value_elem = element.find(_Premis.significantPropertiesValue)
        # All children not type or value are considered extension
        extension = [
            child
            for child in element
            if child.tag
            not in {
                _Premis.significantPropertiesType,
                _Premis.significantPropertiesValue,
            }
        ]
        return cls(
            type=(
                SignificantPropertiesType.from_xml_tree(type_elem)
                if type_elem is not None
                else None
            ),
            value=(
                SignificantPropertiesValue.from_xml_tree(value_elem)
                if value_elem is not None
                else None
            ),
            extension=extension,
        )


@dataclass(kw_only=True)
class ContentLocationType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class ContentLocationValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class ContentLocation:
    type: ContentLocationType
    value: ContentLocationValue
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.contentLocationType)
        if type_elem is None:
            raise ValueError("Missing contentLocationType")
        value_elem = element.find(_Premis.contentLocationValue)
        if value_elem is None:
            raise ValueError("Missing contentLocationValue")
        return cls(
            type=ContentLocationType.from_xml_tree(type_elem),
            value=ContentLocationValue.from_xml_tree(value_elem),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class StorageMedium(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class Storage:
    content_location: ContentLocation | None
    storage_medium: StorageMedium | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        content_location_elem = element.find(_Premis.contentLocation)
        storage_medium_elem = element.find(_Premis.storageMedium)
        return cls(
            content_location=(
                ContentLocation.from_xml_tree(content_location_elem)
                if content_location_elem is not None
                else None
            ),
            storage_medium=(
                StorageMedium.from_xml_tree(storage_medium_elem)
                if storage_medium_elem is not None
                else None
            ),
        )


@dataclass(kw_only=True)
class File:
    xsi_type: Literal["premis:file"]
    identifiers: list[ObjectIdentifier]
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties]
    characteristics: list[ObjectCharacteristics]
    original_name: OriginalName | None
    storages: list[Storage]
    # signature_informations: list[...]
    relationships: list[Relationship]
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        # TODO: expand attribute qname
        xsi_type = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        if xsi_type != "premis:file":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(_Premis.significantProperties)
        ]
        characteristics = [
            ObjectCharacteristics.from_xml_tree(e)
            for e in element.findall(_Premis.objectCharacteristics)
        ]
        original_name_elem = element.find(_Premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        storages = [Storage.from_xml_tree(e) for e in element.findall(_Premis.storage)]
        relationships = [
            Relationship.from_xml_tree(e) for e in element.findall(_Premis.relationship)
        ]
        return cls(
            xsi_type=xsi_type,
            identifiers=identifiers,
            significant_properties=significant_properties,
            characteristics=characteristics,
            original_name=original_name,
            storages=storages,
            relationships=relationships,
        )


@dataclass(kw_only=True)
class Representation:
    xsi_type: Literal["premis:representation"]
    identifiers: list[ObjectIdentifier]
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties]
    original_name: OriginalName | None
    storages: list[Storage]
    relationships: list[Relationship]
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        # TODO: expand attribute qname
        xsi_type = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        if xsi_type != "premis:representation":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(_Premis.significantProperties)
        ]
        original_name_elem = element.find(_Premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        storages = [Storage.from_xml_tree(e) for e in element.findall(_Premis.storage)]
        relationships = [
            Relationship.from_xml_tree(e) for e in element.findall(_Premis.relationship)
        ]
        return cls(
            xsi_type=xsi_type,
            identifiers=identifiers,
            significant_properties=significant_properties,
            original_name=original_name,
            storages=storages,
            relationships=relationships,
        )


@dataclass(kw_only=True)
class Bitstream:
    xsi_type: Literal["premis:bitstream"]

    identifiers: list[ObjectIdentifier]
    significant_properties: list[SignificantProperties]
    characteristics: list[ObjectCharacteristics]
    storages: list[Storage]
    # signature_informations: list[...]
    relationships: list[Relationship]
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        # TODO: expand attribute qname
        xsi_type = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        if xsi_type != "premis:bitstream":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(_Premis.significantProperties)
        ]
        characteristics = [
            ObjectCharacteristics.from_xml_tree(e)
            for e in element.findall(_Premis.objectCharacteristics)
        ]
        storages = [Storage.from_xml_tree(e) for e in element.findall(_Premis.storage)]
        relationships = [
            Relationship.from_xml_tree(e) for e in element.findall(_Premis.relationship)
        ]
        return cls(
            xsi_type=xsi_type,
            identifiers=identifiers,
            significant_properties=significant_properties,
            characteristics=characteristics,
            storages=storages,
            relationships=relationships,
        )


@dataclass(kw_only=True)
class IntellectualEntity:
    xsi_type: Literal["premis:intellectualEntity"]

    identifiers: list[ObjectIdentifier]
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties]
    original_name: OriginalName | None
    # environmentFunction
    # environmentDesignation
    # environmentRegistry
    # environmentExtension
    relationships: list[Relationship]
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))

    @property
    def pid(self):
        return next((id for id in self.identifiers if id.is_pid), None)

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        # TODO: expand attribute qname
        xsi_type = element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        if xsi_type != "premis:intellectualEntity":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(_Premis.significantProperties)
        ]
        original_name_elem = element.find(_Premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        relationships = [
            Relationship.from_xml_tree(e) for e in element.findall(_Premis.relationship)
        ]
        return cls(
            xsi_type=xsi_type,
            identifiers=identifiers,
            significant_properties=significant_properties,
            original_name=original_name,
            relationships=relationships,
        )


Object = File | Representation | IntellectualEntity | Bitstream


########## Agent ##########


@dataclass(kw_only=True)
class AgentIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class AgentIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class AgentIdentifier:
    type: AgentIdentifierType
    value: AgentIdentifierValue

    @property
    def is_uuid(self):
        return self.type.text == "UUID"

    @property
    def is_or_id(self):
        return self.type.text == "MEEMOO-OR-ID"

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.agentIdentifierType)
        if type_elem is None:
            raise ValueError("Missing agentIdentifierType")
        value_elem = element.find(_Premis.agentIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing agentIdentifierValue")
        return cls(
            type=AgentIdentifierType.from_xml_tree(type_elem),
            value=AgentIdentifierValue.from_xml_tree(value_elem),
        )


@dataclass(kw_only=True)
class AgentName(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class AgentType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class Agent:
    identifiers: list[AgentIdentifier]
    name: AgentName
    type: AgentType

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))

    @property
    def or_id(self):
        return next((id for id in self.identifiers if id.is_or_id))

    @property
    def primary_identifier(self):
        try:
            return self.or_id
        except StopIteration:
            pass

        try:
            return self.uuid
        except StopIteration:
            pass

        return next((id for id in self.identifiers))

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        identifiers = [
            AgentIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.agentIdentifier)
        ]
        name_elem = element.find(_Premis.agentName)
        if name_elem is None:
            raise ValueError("Missing agentName")
        type_elem = element.find(_Premis.agentType)
        if type_elem is None:
            raise ValueError("Missing agentType")
        return cls(
            identifiers=identifiers,
            name=AgentName.from_xml_tree(name_elem),
            type=AgentType.from_xml_tree(type_elem),
        )


########## Event ##########


@dataclass(kw_only=True)
class EventIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class EventIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class EventIdentifier:
    type: EventIdentifierType
    value: EventIdentifierValue
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.eventIdentifierType)
        if type_elem is None:
            raise ValueError("Missing eventIdentifierType")
        value_elem = element.find(_Premis.eventIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing eventIdentifierValue")
        return cls(
            type=EventIdentifierType.from_xml_tree(type_elem),
            value=EventIdentifierValue.from_xml_tree(value_elem),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class EventDetail:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class EventDetailInformation:
    detail: EventDetail | None
    # detail_extension: list[EventDetailExtension] = element(default_factory=list)

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        detail_elem = element.find(_Premis.eventDetail)
        return cls(
            detail=(
                EventDetail.from_xml_tree(detail_elem)
                if detail_elem is not None
                else None
            ),
        )


@dataclass(kw_only=True)
class EventOutcomeDetailNote:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class EventOutcomeDetail:
    note: EventOutcomeDetailNote | None
    # extension: list[EventOutcomeExtension] = (default_factory=list)

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        note_elem = element.find(_Premis.eventOutcomeDetailNote)
        return cls(
            note=(
                EventOutcomeDetailNote.from_xml_tree(note_elem)
                if note_elem is not None
                else None
            ),
        )


@dataclass(kw_only=True)
class EventOutcome(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class EventOutcomeInformation:
    outcome: EventOutcome | None
    outcome_detail: list[EventOutcomeDetail]

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        outcome_elem = element.find(_Premis.eventOutcome)
        outcome_details = [
            EventOutcomeDetail.from_xml_tree(e)
            for e in element.findall(_Premis.eventOutcomeDetail)
        ]
        return cls(
            outcome=(
                EventOutcome.from_xml_tree(outcome_elem)
                if outcome_elem is not None
                else None
            ),
            outcome_detail=outcome_details,
        )


@dataclass(kw_only=True)
class LinkingAgentIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class LinkingAgentIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class LinkingAgentRole(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class LinkingAgentIdentifier:
    type: LinkingAgentIdentifierType
    value: LinkingAgentIdentifierValue
    roles: list[LinkingAgentRole]

    # LinkAgentXmlID
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.linkingAgentIdentifierType)
        if type_elem is None:
            raise ValueError("Missing linkingAgentIdentifierType")
        value_elem = element.find(_Premis.linkingAgentIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing linkingAgentIdentifierValue")
        roles = [
            LinkingAgentRole.from_xml_tree(e)
            for e in element.findall(_Premis.linkingAgentRole)
        ]
        return cls(
            type=LinkingAgentIdentifierType.from_xml_tree(type_elem),
            value=LinkingAgentIdentifierValue.from_xml_tree(value_elem),
            roles=roles,
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class LinkingObjectIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class LinkingObjectIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class LinkingObjectRole(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class LinkingObjectIdentifier:
    type: LinkingObjectIdentifierType
    value: LinkingObjectIdentifierValue
    roles: list[LinkingObjectRole]
    # LinkObjectXmlID
    simple_link: str | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(_Premis.linkingObjectIdentifierType)
        if type_elem is None:
            raise ValueError("Missing linkingObjectIdentifierType")
        value_elem = element.find(_Premis.linkingObjectIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing linkingObjectIdentifierValue")
        roles = [
            LinkingObjectRole.from_xml_tree(e)
            for e in element.findall(_Premis.linkingObjectRole)
        ]
        return cls(
            type=LinkingObjectIdentifierType.from_xml_tree(type_elem),
            value=LinkingObjectIdentifierValue.from_xml_tree(value_elem),
            roles=roles,
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class EventType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class EventDateTime:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class Event:
    identifier: EventIdentifier
    type: EventType
    datetime: EventDateTime
    detail_information: list[EventDetailInformation]
    outcome_information: list[EventOutcomeInformation]
    linking_agent_identifiers: list[LinkingAgentIdentifier]
    linking_object_identifiers: list[LinkingObjectIdentifier]

    # xml_id = attr()
    # version: Literal["version3"]

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        identifier_elem = element.find(_Premis.eventIdentifier)
        if identifier_elem is None:
            raise ValueError("Missing eventIdentifier")
        type_elem = element.find(_Premis.eventType)
        if type_elem is None:
            raise ValueError("Missing eventType")
        datetime_elem = element.find(_Premis.eventDateTime)
        if datetime_elem is None:
            raise ValueError("Missing eventDateTime")
        detail_information = [
            EventDetailInformation.from_xml_tree(e)
            for e in element.findall(_Premis.eventDetailInformation)
        ]
        outcome_information = [
            EventOutcomeInformation.from_xml_tree(e)
            for e in element.findall(_Premis.eventOutcomeInformation)
        ]
        linking_agent_identifiers = [
            LinkingAgentIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.linkingAgentIdentifier)
        ]
        linking_object_identifiers = [
            LinkingObjectIdentifier.from_xml_tree(e)
            for e in element.findall(_Premis.linkingObjectIdentifier)
        ]
        return cls(
            identifier=EventIdentifier.from_xml_tree(identifier_elem),
            type=EventType.from_xml_tree(type_elem),
            datetime=EventDateTime.from_xml_tree(datetime_elem),
            detail_information=detail_information,
            outcome_information=outcome_information,
            linking_agent_identifiers=linking_agent_identifiers,
            linking_object_identifiers=linking_object_identifiers,
        )


########## Premis ##########


@dataclass(kw_only=True)
class Premis:
    objects: list[Object]
    events: list[Event]
    agents: list[Agent]
    # rights: lsit[Rights]

    version: Literal["3.0"]

    @property
    def entity(self) -> IntellectualEntity:
        """
        Returns the first object with xsi:type='intellectualEntity' in the PREMIS file.
        """
        return next(
            (obj for obj in self.objects if isinstance(obj, IntellectualEntity))
        )

    @property
    def representation(self):
        """
        Returns the first object with xsi:type='intellectualEntity' in the PREMIS file.
        """
        return next((obj for obj in self.objects if isinstance(obj, Representation)))

    @property
    def files(self):
        """
        Returns all objects with xsi:type='file' in the PREMIS file.
        """
        return [obj for obj in self.objects if isinstance(obj, File)]

    @classmethod
    def from_xml(cls, path: Path | str) -> Self:
        root = ET.parse(path).getroot()
        return cls.from_xml_tree(root)

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        version = element.get("version")
        if version != "3.0":
            raise ValueError()

        events = [
            Event.from_xml_tree(evt) for evt in element if evt.tag == _Premis.event
        ]
        agents = [
            Agent.from_xml_tree(agent)
            for agent in element
            if agent.tag == _Premis.agent
        ]

        return cls(
            version=version,
            objects=cls._parse_objects(element),
            events=events,
            agents=agents,
        )

    @staticmethod
    def _parse_objects(element: Element) -> list[Object]:
        objects = [obj for obj in element if obj.tag == _Premis.object]

        # TODO: expand premis:... to its full URI
        files = (
            File.from_xml_tree(file)
            for file in objects
            if file.get("{http://www.w3.org/2001/XMLSchema-instance}type")
            == "premis:file"
        )

        reprs = (
            Representation.from_xml_tree(repr)
            for repr in objects
            if repr.get("{http://www.w3.org/2001/XMLSchema-instance}type")
            == "premis:representation"
        )

        entities = (
            IntellectualEntity.from_xml_tree(entity)
            for entity in objects
            if entity.get("{http://www.w3.org/2001/XMLSchema-instance}type")
            == "premis:intellectualEntity"
        )

        return list(chain(entities, reprs, files))
