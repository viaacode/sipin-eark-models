import xmlschema
import pytest
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from tests.factory import PremisFactory

schema = xmlschema.XMLSchema("./tests/assets/premis.xsd.xml")


@pytest.fixture(autouse=True)
def set_random_seed():
    """
    Set the random seed before every test fuction call.
    """
    seed = 1
    Faker.seed(seed)
    ModelFactory.__faker__ = Faker()
    ModelFactory.__random__.seed(seed)


def test_premis_serialization_against_xsd():
    premises = PremisFactory.batch(size=200)
    for premis in premises:
        xml = premis.to_xml(skip_empty=True, pretty_print=False)
        assert schema.validate(xml) == None
