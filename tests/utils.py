from typing import Any
import xml.etree.ElementTree as ET
from collections import Counter

import eark_models.namespaces as ns


def count_object_contents(object_instance: object) -> Counter[Any]:
    counter = Counter[Any]()

    is_builtin = object_instance.__class__.__module__ == "builtins"
    is_element = isinstance(object_instance, ET.Element)
    is_iterable = isinstance(object_instance, (list, tuple, set))

    if is_element:
        counter |= count_xml_contents(object_instance)

    elif not is_builtin and not is_element:
        for _, field_value in object_instance.__dict__.items():
            counter |= count_object_contents(field_value)

    elif is_iterable:
        for element in object_instance:
            counter |= count_object_contents(element)

    elif object_instance is not None:
        counter.update([str(object_instance)])

    return counter


def count_xml_contents(element: ET.Element) -> Counter[Any]:
    counter = Counter[Any]()

    for k, v in element.attrib.items():
        if k == ns.xsi.schemaLocation:
            continue

        counter.update([v])

    children = [child for child in element]
    for child in children:
        counter |= count_xml_contents(child)

    if len(children) == 0:
        contents = element.text if element.text is not None else ""
        counter.update([contents])

    return counter
