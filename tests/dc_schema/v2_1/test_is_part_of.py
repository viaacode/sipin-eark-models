from pathlib import Path

import pytest

from eark_models.utils import parse_xml_tree, InvalidXMLError
import eark_models.dc_schema.v2_1 as dc_schema
from eark_models.langstring import _LangString, UniqueLang

cwd = Path(__file__).parent


def test_parsing_with_default_namespace():
    root = parse_xml_tree(cwd / "./samples/is_part_of_default_namespace.xml")
    dc_schema.parse_is_part_of(root)


def test_episode():
    root = parse_xml_tree(cwd / "./samples/is_part_of_episode.xml")
    episode = dc_schema.Episode.from_xml_tree(root)

    assert episode == dc_schema.Episode(
        __source__="",
        xsi_type="{https://schema.org/}Episode",
        name=UniqueLang(
            [
                _LangString(lang="nl", value="SIP.py, het SIP model"),
            ]
        ),
    )


def test_broadcast_event():
    tree = parse_xml_tree(cwd / "./samples/is_part_of_event.xml")
    event = dc_schema.BroadcastEvent.from_xml_tree(tree)

    assert event == dc_schema.BroadcastEvent(
        __source__="",
        xsi_type="{https://schema.org/}BroadcastEvent",
        name=UniqueLang(
            [
                _LangString(lang="nl", value="Eventfully"),
            ]
        ),
    )


def test_parsing_with_custom_namespace():
    root = parse_xml_tree(cwd / "./samples/is_part_of_custom_namespace.xml")
    _ = dc_schema.parse_is_part_of(root)


def test_parsing_without_xsi_type():
    root = parse_xml_tree(cwd / "./samples/is_part_of_without_xsi_type.xml")

    with pytest.raises(InvalidXMLError):
        _ = dc_schema.parse_is_part_of(root)


def test_has_parts_inside_is_part_of():
    root = parse_xml_tree(cwd / "./samples/is_part_of_with_has_part.xml")
    _ = dc_schema.parse_is_part_of(root)
