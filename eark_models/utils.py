from abc import ABC
from typing import cast, TextIO, Self
import xml.etree.ElementTree as ET
from pathlib import Path

from pydantic.dataclasses import dataclass


from .namespaces import xsi
from .etree import _Element


class EarkModelsError(Exception): ...


class InvalidXMLError(EarkModelsError): ...


@dataclass
class XMLParseable(ABC):
    @classmethod
    def from_xml(cls, path: Path) -> Self: ...


def expand_qname_attributes(
    element: ET.Element, document_namespaces: dict[str, str]
) -> ET.Element:
    """
    Certain attributes may have a prefixed value e.g. xsi:type="schema:Episode".
    Expand the prefixed attribute value to its full qualified name e.g. "{https://schema.org/}Episode"
    """

    for k, v in element.attrib.items():
        if k == xsi.type:
            element.attrib[k] = expand_qname(v, document_namespaces)

    for child in element:
        _ = expand_qname_attributes(child, document_namespaces)

    return element


def parse_xml_tree(source: str | Path) -> "_Element":
    document_namespaces = get_document_namespaces(source)
    tree = ET.parse(source)
    expand_qname_attributes(tree.getroot(), document_namespaces)
    return _Element(tree.getroot(), source=str(source))


def expand_qname(name: str, document_namespaces: dict[str, str]) -> str:
    """
    Expand a prefixed qualified name to its fully qualified name.
    E.g. "schema:Episode" is expanded to "{https://schema.org/}Episode"
    """

    has_default_ns = "" in document_namespaces
    has_prefix = ":" in name

    if not has_prefix and not has_default_ns:
        return name

    if not has_prefix and has_default_ns:
        default_ns = document_namespaces[""]
        return "{" + default_ns + "}" + name

    splitted_qname = name.split(":", 1)
    prefix = splitted_qname[0]
    local = splitted_qname[1]
    prefix_iri = document_namespaces[prefix]

    return "{" + prefix_iri + "}" + local


def get_document_namespaces(source: str | Path | TextIO) -> dict[str, str]:
    document_namespaces = [
        ns_tuple for _, ns_tuple in ET.iterparse(source, events=["start-ns"])
    ]
    return dict(cast(list[tuple[str, str]], document_namespaces))
