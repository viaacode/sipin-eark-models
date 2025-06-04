from typing import Literal, Self
from xml.etree.ElementTree import Element

from pydantic import BaseModel


AnyURI = str


class SimpleLink(BaseModel):
    type: Literal["simple"] | None
    href: AnyURI | None
    role: str | None
    arcrole: str | None
    title: str | None
    show: Literal["new", "replace", "embed", "other", "none"] | None
    actuate: Literal["onLoad", "onRequest", "other", "none"] | None

    @classmethod
    def from_xml_tree(cls, root: Element) -> Self:

        # TODO: the attributes below could be using a prefix different from `xlink`
        type = root.attrib.get("xlink:type")
        if type is not None and type != "simple":
            raise ValueError()

        show = root.attrib.get("xlink:show")
        if show is not None and show not in (
            "new",
            "replace",
            "embed",
            "other",
            "none",
        ):
            raise ValueError()

        actuate = root.attrib.get("xlink:actuate")
        if actuate is not None and actuate not in (
            "onLoad",
            "onRequest",
            "other",
            "none",
        ):
            raise ValueError()

        return cls(
            type=type,
            href=root.attrib.get("xlink:href"),
            role=root.attrib.get("xlink:role"),
            arcrole=root.attrib.get("xlink:arcrole"),
            title=root.attrib.get("xlink:title"),
            show=show,
            actuate=actuate,
        )
