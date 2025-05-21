# sipin E-ARK models
Pydantic models for the E-ARK CSIP. Currently only includes PREMIS.

## Usage

Create a PREMIS pydantic model with

```py
from lxml import etree
from eark_models.premis import Premis

root = etree.parse(PATH).getroot()
premis = Premis.from_xml_tree(root)
```

