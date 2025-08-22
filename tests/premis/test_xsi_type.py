from pathlib import Path

from eark_models.premis.v3_0 import Premis
from eark_models.utils import parse_xml_tree

cwd = Path(__file__).parent


def test_file_xsi_type_standard_prefix():
    root = parse_xml_tree(cwd / "./premis_file_with_standard_xsi_type.xml")
    premis = Premis.from_xml_tree(root)

    assert premis.objects[0].xsi_type == "{http://www.loc.gov/premis/v3}file"


def test_file_xsi_type_non_standard_prefix():
    root = parse_xml_tree(cwd / "./premis_file_with_custom_xsi_type.xml")
    premis = Premis.from_xml_tree(root)

    assert premis.objects[0].xsi_type == "{http://www.loc.gov/premis/v3}file"
