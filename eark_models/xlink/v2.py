#                            oooo   o8o              oooo
#                            `888   `"'              `888
#                oooo    ooo  888  oooo  ooo. .oo.    888  oooo
#                 `88b..8P'   888  `888  `888P"Y88b   888 .8P'
#                   Y888'     888   888   888   888   888888.
#                 .o8"'88b    888   888   888   888   888 `88b.
#                o88'   888o o888o o888o o888o o888o o888o o888o


from typing import Literal, TypedDict
from xml.etree.ElementTree import Element

from eark_models.utils import InvalidXMLError

AnyURI = str


class SimpleLink(TypedDict):
    xlink_type: Literal["simple"] | None
    xlink_href: AnyURI | None
    xlink_role: str | None
    xlink_arcrole: str | None
    xlink_title: str | None
    xlink_show: Literal["new", "replace", "embed", "other", "none"] | None
    xlink_actuate: Literal["onLoad", "onRequest", "other", "none"] | None


def parse_simple_link(root: Element) -> SimpleLink:
    # TODO: the attributes below could be using a prefix different from `xlink`
    type = root.attrib.get("xlink:type")
    if type is not None and type != "simple":
        raise InvalidXMLError()

    show = root.attrib.get("xlink:show")
    if show is not None and show not in (
        "new",
        "replace",
        "embed",
        "other",
        "none",
    ):
        raise InvalidXMLError()

    actuate = root.attrib.get("xlink:actuate")
    if actuate is not None and actuate not in (
        "onLoad",
        "onRequest",
        "other",
        "none",
    ):
        raise InvalidXMLError()

    return {
        "xlink_type": type,
        "xlink_href": root.attrib.get("xlink:href"),
        "xlink_role": root.attrib.get("xlink:role"),
        "xlink_arcrole": root.attrib.get("xlink:arcrole"),
        "xlink_title": root.attrib.get("xlink:title"),
        "xlink_show": show,
        "xlink_actuate": actuate,
    }
