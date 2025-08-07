from io import StringIO

import pytest

from eark_models.utils import parse_xml_tree, InvalidXMLError
import eark_models.dc_schema.v2_1 as dc_schema
from eark_models.langstring import _LangString, UniqueLang


def test_parsing_with_default_namespace():
    content = r"""<schema:isPartOf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schema="https://schema.org/" xsi:type="schema:Episode">
        <schema:name xml:lang="nl">SIP.py, het SIP model</schema:name></schema:isPartOf>"""

    file = StringIO(content)
    root = parse_xml_tree(file)
    dc_schema.parse_is_part_of(root)


def test_episode():
    content = """<schema:isPartOf  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schema="https://schema.org/"
      xsi:type="schema:Episode">
      <schema:name xml:lang="nl">SIP.py, het SIP model</schema:name>
    </schema:isPartOf>
    """

    file = StringIO(content)
    root = parse_xml_tree(file)
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
    content = """<myschema:isPartOf  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:myschema="https://schema.org/"
      xsi:type="myschema:BroadcastEvent">
      <myschema:name xml:lang="nl">Eventfully</myschema:name>
    </myschema:isPartOf>
    """

    file = StringIO(content)
    tree = parse_xml_tree(file)
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


def test_parsing_with_non_default_namespace():
    content = """<myschema:isPartOf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:myschema="https://schema.org/"
      xsi:type="myschema:BroadcastEvent">
      <myschema:name xml:lang="nl">Eventfully</myschema:name>
    </myschema:isPartOf>
    """

    file = StringIO(content)
    root = parse_xml_tree(file)
    _ = dc_schema.parse_is_part_of(root)


def test_parsing_without_xsi_type():
    content = """<schema:isPartOf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schema="https://schema.org/">
      <schema:name xml:lang="nl">SIP.py, the SIP model</schema:name>
    </schema:isPartOf>
    """

    file = StringIO(content)
    root = parse_xml_tree(file)

    with pytest.raises(InvalidXMLError):
        _ = dc_schema.parse_is_part_of(root)


def test_parsing_with_empty_xsi_type():
    content = """<schema:isPartOf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schema="https://schema.org/"
        xsi:type="">
      <schema:name xml:lang="nl">SIP.py, the SIP model</schema:name>
    </schema:isPartOf>
    """

    file = StringIO(content)
    root = parse_xml_tree(file)

    with pytest.raises(InvalidXMLError):
        _ = dc_schema.parse_is_part_of(root)


def test_has_parts_inside_is_part_of():
    content = """<schema:isPartOf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:schema="https://schema.org/"
        xsi:type="schema:CreativeWorkSeries">
      <schema:name xml:lang="nl">my creative work series</schema:name>
      <schema:hasPart>
          <schema:name xml:lang="nl">has part</schema:name>
      </schema:hasPart>
      <schema:hasPart>
          <schema:name xml:lang="nl">has part 2</schema:name>
      </schema:hasPart>
    </schema:isPartOf>
    """

    file = StringIO(content)
    root = parse_xml_tree(file)
    _ = dc_schema.parse_is_part_of(root)
