from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use

from eark_models.premis import (
    FormatDesignation,
    Premis,
    SignificantProperties,
    Storage,
    StringPlusAuthority,
    Format,
)


class StringPlusAuthorityFactory(ModelFactory[StringPlusAuthority]): ...


class SignificantPropertiesFactory(ModelFactory[SignificantProperties]):
    __set_as_default_factory_for_type__ = True
    extension = []


class DesignationFactory(ModelFactory[FormatDesignation]): ...


class FormatFactory(ModelFactory[Format]):
    __set_as_default_factory_for_type__ = True

    # Format must have at least a designation or a registry
    # Designation is always populated here
    designation = Use(DesignationFactory.build)


class StorageFactory(ModelFactory[Storage]):
    __set_as_default_factory_for_type__ = True

    content_location = None
    storage_medium = Use(StringPlusAuthorityFactory.build)


class PremisFactory(ModelFactory[Premis]):
    pass
