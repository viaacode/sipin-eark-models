from io import StringIO

from eark_models.premis.v3_0 import Premis
from eark_models.utils import parse_xml_tree


def test_file_xsi_type_standard_prefix():
    content = r"""
        <premis:premis version="3.0"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:premis="http://www.loc.gov/premis/v3">
            <premis:object xsi:type="premis:file">
                <premis:objectIdentifier>
                    <premis:objectIdentifierType>UUID</premis:objectIdentifierType>
                    <premis:objectIdentifierValue>uuid-0001</premis:objectIdentifierValue>
                </premis:objectIdentifier>
                <premis:objectCharacteristics>
                    <premis:format>
                        <premis:formatName>CSIP</premis:formatName>
                        <premis:formatVersion>1.0</premis:formatVersion>
                    </premis:format>
                </premis:objectCharacteristics>
            </premis:object>
        </premis:premis>"""

    file = StringIO(content)
    root = parse_xml_tree(file).getroot()
    premis = Premis.from_xml_tree(root)

    assert premis.objects[0].xsi_type == "{http://www.loc.gov/premis/v3}file"


def test_file_xsi_type_non_standard_prefix():
    content = r"""
        <premis3:premis version="3.0"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:premis3="http://www.loc.gov/premis/v3">
            <premis3:object xsi:type="premis3:file">
                <premis3:objectIdentifier>
                    <premis3:objectIdentifierType>UUID</premis3:objectIdentifierType>
                    <premis3:objectIdentifierValue>uuid-0001</premis3:objectIdentifierValue>
                </premis3:objectIdentifier>
                <premis3:objectCharacteristics>
                    <premis3:format>
                        <premis3:formatName>CSIP</premis3:formatName>
                        <premis3:formatVersion>1.0</premis3:formatVersion>
                    </premis3:format>
                </premis3:objectCharacteristics>
            </premis3:object>
        </premis3:premis>"""

    file = StringIO(content)
    root = parse_xml_tree(file).getroot()
    premis = Premis.from_xml_tree(root)

    assert premis.objects[0].xsi_type == "{http://www.loc.gov/premis/v3}file"
