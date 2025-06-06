from typing import Literal, Tuple
from lxml.etree import _Element

from pydantic_xml import BaseXmlModel, attr, element

ns = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "premis": "http://www.loc.gov/premis/v3",
}


class PremisBaseModel(
    BaseXmlModel,
    ns="premis",
    nsmap=ns,
    frozen=True,
    arbitrary_types_allowed=True,
):
    pass


class StringPlusAuthority(BaseXmlModel, frozen=True):
    authority: str | None = attr(default=None)
    authority_uri: str | None = attr(name="authorityURI", default=None)
    innerText: str
    value_uri: str | None = attr(name="valueURI", default=None)


########## Object ##########


class ObjectIdentifier(PremisBaseModel, tag="objectIdentifier", frozen=True):
    type: StringPlusAuthority = element(tag="objectIdentifierType", ns="premis")
    value: str = element(tag="objectIdentifierValue", ns="premis")
    simple_link: str | None = attr(name="simpleLink", default=None)

    @property
    def is_uuid(self):
        return self.type.innerText == "UUID"

    @property
    def is_pid(self):
        return self.type.innerText == "MEEMOO-PID"

    @property
    def is_primary_identifier(self):
        return self.type.innerText == "MEEMOO-LOCAL-ID"

    @property
    def is_local_identifier(self):
        return (
            self.type.innerText != "UUID"
            and self.type.innerText != "MEEMOO-PID"
            and self.type.innerText != "MEEMOO-LOCAL-ID"
        )


class Fixity(PremisBaseModel, tag="fixity", frozen=True):
    message_digest_algorithm: StringPlusAuthority = element(
        tag="messageDigestAlgorithm", ns="premis"
    )
    message_digest: str = element(tag="messageDigest", ns="premis")
    message_digest_originator: StringPlusAuthority | None = element(
        tag="messageDigestOriginator", ns="premis", default=None
    )


class FormatDesignation(PremisBaseModel, tag="formatDesignation", frozen=True):
    name: StringPlusAuthority = element(tag="formatName", ns="premis")
    version: str | None = element(tag="formatVersion", ns="premis", default=None)


class FormatRegistry(PremisBaseModel, tag="formatRegistry", frozen=True):
    name: StringPlusAuthority = element(tag="formatRegistryName", ns="premis")
    key: StringPlusAuthority = element(tag="formatRegistryKey", ns="premis")
    role: StringPlusAuthority | None = element(
        tag="formatRegistryRole", ns="premis", default=None
    )
    simple_link: str | None = attr(name="simpleLink", default=None)


class Format(PremisBaseModel, tag="format", frozen=True):
    designation: FormatDesignation | None = element(default=None)
    registry: FormatRegistry | None = element(default=None)
    note: list[str] = element(tag="formatNote", ns="premis", default_factory=list)


class ObjectCharacteristics(PremisBaseModel, tag="objectCharacteristics", frozen=True):
    # composition_level: ...
    fixity: list[Fixity] = element(default_factory=list)
    size: int | None = element(tag="size", ns="premis", default=None)
    format: list[Format] = element(min_length=1)
    # creating_application: ...
    # inhibitors: ...
    # object_characteristics_extension: ...


class OriginalName(PremisBaseModel, tag="originalName", frozen=True):
    value: str
    simple_link: str | None = attr(name="simpleLink", default=None)


class RelatedObjectIdentifier(
    PremisBaseModel, tag="relatedObjectIdentifier", frozen=True
):
    type: StringPlusAuthority = element(tag="relatedObjectIdentifierType", ns="premis")
    value: str = element(tag="relatedObjectIdentifierValue", ns="premis")
    # sequence: ... | None
    # RelObjectXmlID
    simple_link: str | None = attr(name="simpleLink", default=None)


class Relationship(PremisBaseModel, tag="relationship", frozen=True):
    type: StringPlusAuthority = element(tag="relationshipType", ns="premis")
    sub_type: StringPlusAuthority = element(tag="relationshipSubType", ns="premis")
    related_object_identifier: list[RelatedObjectIdentifier] = element(min_length=1)
    # related_event_identifier: list[...] = element(default_factory=list)
    # related_environment_purpose: list[...] = element(default_factory=list)
    # related_environment_characteristic: list[...] | None = element(default=None)

    @property
    def related_object_uuid(self) -> str:
        return next(
            (
                id.value
                for id in self.related_object_identifier
                if id.type.innerText == "UUID"
            )
        )


class SignificantProperties(PremisBaseModel, tag="significantProperties", frozen=True):
    type: StringPlusAuthority | None = element(
        tag="significantPropertiesType", ns="premis", default=None
    )
    value: str | None = element(
        tag="significantPropertiesValue", ns="premis", default=None
    )
    extension: list[_Element] = element(
        tag="significantPropertiesExtension", ns="premis", default_factory=list
    )


class ContentLocation(PremisBaseModel, tag="contentLocation", frozen=True):
    type: StringPlusAuthority = element(tag="contentLocationType", ns="premis")
    value: str = element(tag="contentLocationValue", ns="premis")

    simple_link: str | None = attr(name="simpleLink", default=None)


class Storage(PremisBaseModel, tag="storage", frozen=True):
    content_location: ContentLocation | None = element(default=None)
    storage_medium: StringPlusAuthority | None = element(
        tag="storageMedium", ns="premis", default=None
    )


class File(PremisBaseModel, tag="object", frozen=True):
    xsi_type: Literal["premis:file"] = attr(name="type", ns="xsi")

    identifiers: list[ObjectIdentifier] = element(min_length=1)
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties] = element(default_factory=list)
    characteristics: list[ObjectCharacteristics] = element(min_length=1)
    original_name: OriginalName | None = element(default=None)
    storages: list[Storage] = element(default_factory=list)
    # signature_informations: list[...]
    relationships: list[Relationship] = element(default_factory=list)
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))


class Representation(PremisBaseModel, tag="object", frozen=True):
    xsi_type: Literal["premis:representation"] = attr(name="type", ns="xsi")

    identifiers: list[ObjectIdentifier] = element(min_length=1)
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties] = element(default_factory=list)
    original_name: OriginalName | None = element(default=None)
    storages: list[Storage] = element(default_factory=list)
    relationships: list[Relationship] = element(default_factory=list)
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))


class Bitstream(PremisBaseModel, tag="object", frozen=True):
    xsi_type: Literal["premis:bitstream"] = attr(name="type", ns="xsi")

    identifiers: list[ObjectIdentifier] = element(min_length=1)
    significant_properties: list[SignificantProperties] = element(default_factory=list)
    characteristics: list[ObjectCharacteristics] = element(min_length=1)
    storages: list[Storage] = element(default_factory=list)
    # signature_informations: list[...]
    relationships: list[Relationship] = element(default_factory=list)
    # linking_event_identifiers: list[...]
    # linking_rights_statement_identifiers: list[...]

    # xml_id: ... = attr()
    # version: Literal["version3"] = attr()

    @property
    def uuid(self):
        return next((id for id in self.identifiers if id.is_uuid))


class IntellectualEntity(PremisBaseModel, tag="object", frozen=True):
    xsi_type: Literal["premis:intellectualEntity"] = attr(name="type", ns="xsi")

    identifiers: list[ObjectIdentifier] = element(min_length=1)
    # preservation_levels: list[PreservationLevel] = element(default_factory=list)
    significant_properties: list[SignificantProperties] = element(default_factory=list)
    original_name: OriginalName | None = element(default=None)
    # environmentFunction
    # environmentDesignation
    # environmentRegistry
    # environmentExtension
    relationships: list[Relationship] = element(default_factory=list)
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


Object = File | Representation | IntellectualEntity | Bitstream


########## Agent ##########


class AgentIdentifier(PremisBaseModel, tag="agentIdentifier", frozen=True):
    type: StringPlusAuthority = element(tag="agentIdentifierType", ns="premis")
    value: str = element(tag="agentIdentifierValue", ns="premis")

    @property
    def is_uuid(self):
        return self.type.innerText == "UUID"

    @property
    def is_or_id(self):
        return self.type.innerText == "MEEMOO-OR-ID"


class Agent(PremisBaseModel, tag="agent", frozen=True):
    identifiers: list[AgentIdentifier] = element(min_length=1)
    name: StringPlusAuthority = element(tag="agentName", ns="premis")
    type: StringPlusAuthority = element(tag="agentType", ns="premis")

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


########## Event ##########


class EventIdentifier(PremisBaseModel, tag="eventIdentifier", frozen=True):
    type: StringPlusAuthority = element(tag="eventIdentifierType", ns="premis")
    value: str = element(tag="eventIdentifierValue", ns="premis")
    simple_link: str | None = attr(name="simpleLink", default=None)


class EventDetailInformation(
    PremisBaseModel, tag="eventDetailInformation", frozen=True
):
    detail: str | None = element(tag="eventDetail", ns="premis", default=None)
    # detail_extension: list[EventDetailExtension] = element(default_factory=list)


class EventOutcomeDetail(PremisBaseModel, tag="eventOutcomeDetail", frozen=True):
    note: str | None = element(tag="eventOutcomeDetailNote", ns="premis", default=None)
    # extension: list[EventOutcomeExtension] = (default_factory=list)


class EventOutcomeInformation(
    PremisBaseModel, tag="eventOutcomeInformation", frozen=True
):
    outcome: StringPlusAuthority | None = element(
        tag="eventOutcome", ns="premis", default=None
    )
    outcome_detail: list[EventOutcomeDetail] = element(default_factory=list)


class LinkingAgentIdentifier(
    PremisBaseModel, tag="linkingAgentIdentifier", frozen=True
):
    type: StringPlusAuthority = element(tag="linkingAgentIdentifierType", ns="premis")
    value: str = element(tag="linkingAgentIdentifierValue", ns="premis")
    roles: Tuple[StringPlusAuthority, ...] = element(
        tag="linkingAgentRole", ns="premis", default_factory=tuple
    )

    # LinkAgentXmlID
    simple_link: str | None = attr(name="simpleLink", default=None)


class LinkingObjectIdentifier(
    PremisBaseModel, tag="linkingObjectIdentifier", frozen=True
):
    type: StringPlusAuthority = element(tag="linkingObjectIdentifierType", ns="premis")
    value: str = element(tag="linkingObjectIdentifierValue", ns="premis")
    roles: tuple[StringPlusAuthority, ...] = element(
        tag="linkingObjectRole", ns="premis", default_factory=tuple
    )

    # LinkObjectXmlID
    simple_link: str | None = attr(name="simpleLink", default=None)


class Event(PremisBaseModel, tag="event", frozen=True):
    identifier: EventIdentifier
    type: StringPlusAuthority = element(tag="eventType", ns="premis")
    datetime: str = element(tag="eventDateTime", ns="premis")
    detail_information: list[EventDetailInformation] = element(default_factory=list)
    outcome_information: list[EventOutcomeInformation] = element(default_factory=list)
    linking_agent_identifiers: list[LinkingAgentIdentifier] = element(
        default_factory=list
    )
    linking_object_identifiers: list[LinkingObjectIdentifier] = element(
        default_factory=list
    )

    # xml_id = attr()
    # version: Literal["version3"]


########## Premis ##########


class Premis(PremisBaseModel, tag="premis", frozen=True):
    objects: list[Object] = element(default_factory=list, min_legnth=1)
    events: list[Event] = element(default_factory=list)
    agents: list[Agent] = element(default_factory=list)

    version: Literal["3.0"] = attr(name="version")

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
