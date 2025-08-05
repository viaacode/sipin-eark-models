from typing import Self

from pydantic.dataclasses import dataclass

from .etree import _Element


@dataclass
class LangString:
    lang: str
    value: str

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        lang = element.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is None:
            raise ValueError()
        return cls(
            lang=lang,
            value=element.text if element.text is not None else "",
        )


def langstrings(element: _Element, path: str) -> list[LangString]:
    elements = element.findall(path)
    return [LangString.from_xml_tree(el) for el in elements]
