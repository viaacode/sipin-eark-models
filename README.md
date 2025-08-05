# sipin E-ARK models
Pydantic models for the E-ARK CSIP. Currently only includes PREMIS.

## Usage

Create a PREMIS pydantic model with

```py
from eark_models.premis.v3_0 import Premis

premis = Premis.from_xml("premis.xml")
```

