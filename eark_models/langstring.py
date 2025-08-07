from typing import Self, Callable, NewType

from pydantic.dataclasses import dataclass

from eark_models.utils import InvalidXMLError

from .etree import _Element


@dataclass(frozen=True)
class _LangString:
    lang: str
    value: str

    @classmethod
    def from_xml_tree(cls, element: _Element) -> Self:
        lang = element.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is None:
            raise InvalidXMLError("Missing language tag on langstring.")
        return cls(
            lang=lang,
            value=element.text if element.text is not None else "",
        )


UniqueLang = NewType("UniqueLang", list[_LangString])
"""A set of langstrings with the unique language tag"""

LangStrings = NewType("LangStrings", list[_LangString])
"""A set of langstrings without the unqiue language tag"""


def langstrings(element: _Element, path: str) -> LangStrings:
    elements = element.findall(path)
    lang_strings = [_LangString.from_xml_tree(el) for el in elements]

    if len(lang_strings) == 0:
        return LangStrings([])

    has_nl = any(string for string in lang_strings if string.lang == "nl")
    if not has_nl:
        raise InvalidXMLError(
            f"The element '{path}' is missing a obligatory language tagged string with value 'nl'. Every set of language string must contain a language string with language 'nl'."
        )

    return LangStrings(lang_strings)


def duplicate_by_key[T, K](input: list[T], key_func: Callable[[T], K]) -> list[T]:
    seen = set[K]()
    result = []
    for item in input:
        key = key_func(item)
        if key in seen:
            result.append(item)
        if key not in seen:
            seen.add(key)
    return result


def unique_by_key[T, K](input: list[T], key_func: Callable[[T], K]) -> list[T]:
    seen = set[K]()
    result = []
    for item in input:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def unique_lang(element: _Element, path: str) -> UniqueLang:
    lang_strings = langstrings(element, path)
    duplicate_lang_strings = duplicate_by_key(lang_strings, lambda string: string.lang)

    if len(duplicate_lang_strings) > 0:
        raise InvalidXMLError(
            f"The element '{path}' contains duplicate language tag(s) '{' ,'.join(string.lang for string in duplicate_lang_strings)}'. Every language tag must only appear once for a set of language strings tagged with unique language tag contstraint."
        )
    return UniqueLang(unique_by_key(lang_strings, lambda string: string.lang))
