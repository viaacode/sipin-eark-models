from typing import Generator
import xml.etree.ElementTree as ET


class _Element:
    "Wrapper around ET.Element that adds a __source__ attribute."

    __source__: str

    def __init__(self, element: ET.Element, *, source: str):
        self.element = element
        self.__source__ = source

    def find(
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "_Element | None":
        element = self.element.find(path, namespaces)
        if element is None:
            return None
        return _Element(element, source=self.__source__)

    def findall(
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "list[_Element]":
        elements = self.element.findall(path, namespaces)
        return [_Element(el, source=self.__source__) for el in elements]

    def findtext(
        self, path: str, default: None = None, namespaces: dict[str, str] | None = None
    ) -> str | None:
        return self.element.findtext(path, default, namespaces)

    @property
    def text(self) -> str | None:
        return self.element.text

    @property
    def tag(self) -> str:
        return self.element.tag

    @property
    def attrib(self) -> dict[str, str]:
        return self.element.attrib

    def get[_T](self, key: str, default: _T = None) -> str | _T:
        return self.element.get(key, default)

    def __iter__(self) -> "Generator[_Element, None, None]":
        for child in self.element:
            yield _Element(child, source=self.__source__)
