from typing import Literal, Self
from pathlib import Path
from itertools import chain
from xml.etree.ElementTree import Element

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from eark_models.utils import parse_xml_tree
import eark_models.namespaces as ns

AnyURI = str


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
    simple_link: AnyURI | None

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
        type = element.find(ns.premis.objectIdentifierType)
        if type is None:
            raise ValueError()
        value = element.find(ns.premis.objectIdentifierValue)
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
        algo_elem = element.find(ns.premis.messageDigestAlgorithm)
        if algo_elem is None:
            raise ValueError("Missing messageDigestAlgorithm")
        digest_elem = element.find(ns.premis.messageDigest)
        if digest_elem is None:
            raise ValueError("Missing messageDigest")
        originator_elem = element.find(ns.premis.messageDigestOriginator)

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
        name_elem = element.find(ns.premis.formatName)
        if name_elem is None:
            raise ValueError("Missing formatName")
        version_elem = element.find(ns.premis.formatVersion)
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
    simple_link: AnyURI | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        name_elem = element.find(ns.premis.formatRegistryName)
        if name_elem is None:
            raise ValueError("Missing formatRegistryName")
        key_elem = element.find(ns.premis.formatRegistryKey)
        if key_elem is None:
            raise ValueError("Missing formatRegistryKey")
        role_elem = element.find(ns.premis.formatRegistryRole)
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
        designation_elem = element.find(ns.premis.formatDesignation)
        registry_elem = element.find(ns.premis.formatRegistry)
        notes = [
            FormatNote.from_xml_tree(note_elem)
            for note_elem in element.findall(ns.premis.formatNote)
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
    value: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            raise ValueError("Size element has no text")
        return cls(value=element.text)


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
            for fix_elem in element.findall(ns.premis.fixity)
        ]
        size_elem = element.find(ns.premis.size)
        formats = [
            Format.from_xml_tree(fmt_elem)
            for fmt_elem in element.findall(ns.premis.format)
        ]
        return cls(
            fixity=fixities,
            size=Size.from_xml_tree(size_elem) if size_elem is not None else None,
            format=formats,
        )


@dataclass(kw_only=True)
class OriginalName:
    text: str
    simple_link: AnyURI | None

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
    simple_link: AnyURI | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(ns.premis.relatedObjectIdentifierType)
        if type_elem is None:
            raise ValueError("Missing relatedObjectIdentifierType")
        value_elem = element.find(ns.premis.relatedObjectIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing relatedObjectIdentifierValue")
        return cls(
            type=RelatedObjectIdentifierType.from_xml_tree(type_elem),
            value=RelatedObjectIdentifierValue.from_xml_tree(value_elem),
            simple_link=element.get("simpleLink"),
        )


@dataclass(kw_only=True)
class RelatedEventIdentifierType(StringPlusAuthority):
    pass


@dataclass(kw_only=True)
class RelatedEventIdentifierValue:
    text: str

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        if element.text is None:
            return cls(text="")
        return cls(text=element.text)


@dataclass(kw_only=True)
class RelatedEventIdentifier:
    type: RelatedEventIdentifierType
    value: RelatedEventIdentifierValue
    # sequence: RelatedEventSequence
    # RelEventXmlID: IDRef
    simple_link: AnyURI | None

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        type_elem = element.find(ns.premis.relatedEventIdentifierType)
        if type_elem is None:
            raise ValueError("Missing relatedEventIdentifierType")
        value_elem = element.find(ns.premis.relatedEventIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing relatedEventIdentifierValue")
        return cls(
            type=RelatedEventIdentifierType.from_xml_tree(type_elem),
            value=RelatedEventIdentifierValue.from_xml_tree(value_elem),
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
    related_event_identifier: list[RelatedEventIdentifier]

    # TODO
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
        type_elem = element.find(ns.premis.relationshipType)
        if type_elem is None:
            raise ValueError("Missing relationshipType")
        sub_type_elem = element.find(ns.premis.relationshipSubType)
        if sub_type_elem is None:
            raise ValueError("Missing relationshipSubType")
        related_object_elements = element.findall(ns.premis.relatedObjectIdentifier)
        related_object_identifiers = [
            RelatedObjectIdentifier.from_xml_tree(e) for e in related_object_elements
        ]
        related_event_elements = element.findall(ns.premis.relatedEventIdentifier)
        related_event_identifiers = [
            RelatedEventIdentifier.from_xml_tree(e) for e in related_event_elements
        ]
        return cls(
            type=RelationshipType.from_xml_tree(type_elem),
            sub_type=RelationshipSubType.from_xml_tree(sub_type_elem),
            related_object_identifier=related_object_identifiers,
            related_event_identifier=related_event_identifiers,
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
        type_elem = element.find(ns.premis.significantPropertiesType)
        value_elem = element.find(ns.premis.significantPropertiesValue)
        # All children not type or value are considered extension
        extension = [
            child
            for child in element
            if child.tag
            not in {
                ns.premis.significantPropertiesType,
                ns.premis.significantPropertiesValue,
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
        type_elem = element.find(ns.premis.contentLocationType)
        if type_elem is None:
            raise ValueError("Missing contentLocationType")
        value_elem = element.find(ns.premis.contentLocationValue)
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
        content_location_elem = element.find(ns.premis.contentLocation)
        storage_medium_elem = element.find(ns.premis.storageMedium)
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
    xsi_type: Literal["{http://www.loc.gov/premis/v3}file"]
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
        xsi_type = element.get(ns.xsi.type)
        if xsi_type != "{http://www.loc.gov/premis/v3}file":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(ns.premis.significantProperties)
        ]
        characteristics = [
            ObjectCharacteristics.from_xml_tree(e)
            for e in element.findall(ns.premis.objectCharacteristics)
        ]
        original_name_elem = element.find(ns.premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        storages = [
            Storage.from_xml_tree(e) for e in element.findall(ns.premis.storage)
        ]
        relationships = [
            Relationship.from_xml_tree(e)
            for e in element.findall(ns.premis.relationship)
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
    xsi_type: Literal["{http://www.loc.gov/premis/v3}representation"]
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
        xsi_type = element.get(ns.xsi.type)
        if xsi_type != "{http://www.loc.gov/premis/v3}representation":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(ns.premis.significantProperties)
        ]
        original_name_elem = element.find(ns.premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        storages = [
            Storage.from_xml_tree(e) for e in element.findall(ns.premis.storage)
        ]
        relationships = [
            Relationship.from_xml_tree(e)
            for e in element.findall(ns.premis.relationship)
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
    xsi_type: Literal["{http://www.loc.gov/premis/v3}bitstream"]

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
        xsi_type = element.get(ns.xsi.type)
        if xsi_type != "{http://www.loc.gov/premis/v3}bitstream":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(ns.premis.significantProperties)
        ]
        characteristics = [
            ObjectCharacteristics.from_xml_tree(e)
            for e in element.findall(ns.premis.objectCharacteristics)
        ]
        storages = [
            Storage.from_xml_tree(e) for e in element.findall(ns.premis.storage)
        ]
        relationships = [
            Relationship.from_xml_tree(e)
            for e in element.findall(ns.premis.relationship)
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
    xsi_type: Literal["{http://www.loc.gov/premis/v3}intellectualEntity"]

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
        xsi_type = element.get(ns.xsi.type)
        if xsi_type != "{http://www.loc.gov/premis/v3}intellectualEntity":
            raise ValueError()
        identifiers = [
            ObjectIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.objectIdentifier)
        ]
        significant_properties = [
            SignificantProperties.from_xml_tree(e)
            for e in element.findall(ns.premis.significantProperties)
        ]
        original_name_elem = element.find(ns.premis.originalName)
        original_name = (
            OriginalName.from_xml_tree(original_name_elem)
            if original_name_elem is not None
            else None
        )
        relationships = [
            Relationship.from_xml_tree(e)
            for e in element.findall(ns.premis.relationship)
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
        type_elem = element.find(ns.premis.agentIdentifierType)
        if type_elem is None:
            raise ValueError("Missing agentIdentifierType")
        value_elem = element.find(ns.premis.agentIdentifierValue)
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
    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    identifiers: list[AgentIdentifier]
    name: AgentName
    type: AgentType
    extension: list[Element]

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
            for e in element.findall(ns.premis.agentIdentifier)
        ]
        name_elem = element.find(ns.premis.agentName)
        if name_elem is None:
            raise ValueError("Missing agentName")
        type_elem = element.find(ns.premis.agentType)
        if type_elem is None:
            raise ValueError("Missing agentType")
        extension = [
            child
            for child in element
            if child.tag
            not in {
                ns.premis.agentIdentifier,
                ns.premis.agentName,
                ns.premis.agentType,
            }
        ]
        return cls(
            identifiers=identifiers,
            name=AgentName.from_xml_tree(name_elem),
            type=AgentType.from_xml_tree(type_elem),
            extension=extension,
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
        type_elem = element.find(ns.premis.eventIdentifierType)
        if type_elem is None:
            raise ValueError("Missing eventIdentifierType")
        value_elem = element.find(ns.premis.eventIdentifierValue)
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
    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    detail: EventDetail | None
    extension: list[Element]

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        detail_elem = element.find(ns.premis.eventDetail)
        extension = [
            child for child in element if child.tag not in {ns.premis.eventDetail}
        ]
        return cls(
            detail=(
                EventDetail.from_xml_tree(detail_elem)
                if detail_elem is not None
                else None
            ),
            extension=extension,
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
        note_elem = element.find(ns.premis.eventOutcomeDetailNote)
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
        outcome_elem = element.find(ns.premis.eventOutcome)
        outcome_details = [
            EventOutcomeDetail.from_xml_tree(e)
            for e in element.findall(ns.premis.eventOutcomeDetail)
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
        type_elem = element.find(ns.premis.linkingAgentIdentifierType)
        if type_elem is None:
            raise ValueError("Missing linkingAgentIdentifierType")
        value_elem = element.find(ns.premis.linkingAgentIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing linkingAgentIdentifierValue")
        roles = [
            LinkingAgentRole.from_xml_tree(e)
            for e in element.findall(ns.premis.linkingAgentRole)
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
        type_elem = element.find(ns.premis.linkingObjectIdentifierType)
        if type_elem is None:
            raise ValueError("Missing linkingObjectIdentifierType")
        value_elem = element.find(ns.premis.linkingObjectIdentifierValue)
        if value_elem is None:
            raise ValueError("Missing linkingObjectIdentifierValue")
        roles = [
            LinkingObjectRole.from_xml_tree(e)
            for e in element.findall(ns.premis.linkingObjectRole)
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
        identifier_elem = element.find(ns.premis.eventIdentifier)
        if identifier_elem is None:
            raise ValueError("Missing eventIdentifier")
        type_elem = element.find(ns.premis.eventType)
        if type_elem is None:
            raise ValueError("Missing eventType")
        datetime_elem = element.find(ns.premis.eventDateTime)
        if datetime_elem is None:
            raise ValueError("Missing eventDateTime")
        detail_information = [
            EventDetailInformation.from_xml_tree(e)
            for e in element.findall(ns.premis.eventDetailInformation)
        ]
        outcome_information = [
            EventOutcomeInformation.from_xml_tree(e)
            for e in element.findall(ns.premis.eventOutcomeInformation)
        ]
        linking_agent_identifiers = [
            LinkingAgentIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.linkingAgentIdentifier)
        ]
        linking_object_identifiers = [
            LinkingObjectIdentifier.from_xml_tree(e)
            for e in element.findall(ns.premis.linkingObjectIdentifier)
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
        tree = parse_xml_tree(path)
        return cls.from_xml_tree(tree.getroot())

    @classmethod
    def from_xml_tree(cls, element: Element) -> Self:
        version = element.get("version")
        if version != "3.0":
            raise ValueError()

        events = [
            Event.from_xml_tree(evt) for evt in element if evt.tag == ns.premis.event
        ]
        agents = [
            Agent.from_xml_tree(agent)
            for agent in element
            if agent.tag == ns.premis.agent
        ]

        return cls(
            version=version,
            objects=cls._parse_objects(element),
            events=events,
            agents=agents,
        )

    @staticmethod
    def _parse_objects(element: Element) -> list[Object]:
        objects = [obj for obj in element if obj.tag == ns.premis.object]

        files = (
            File.from_xml_tree(file)
            for file in objects
            if file.get(ns.xsi.type) == ns.premis.file
        )

        reprs = (
            Representation.from_xml_tree(repr)
            for repr in objects
            if repr.get(ns.xsi.type) == ns.premis.representation
        )

        entities = (
            IntellectualEntity.from_xml_tree(entity)
            for entity in objects
            if entity.get(ns.xsi.type) == ns.premis.intellectualEntity
        )

        return list(chain(entities, reprs, files))
