from pathlib import Path

import pytest
from eark_models.sip.v2_2_0 import SIP
from eark_models.dc_schema.v2_1 import DCPlusSchema


examples_path = Path("tests/sip-examples")
sip_paths = list(examples_path.joinpath("2.1").iterdir())

excludes = [
    "tests/sip-examples/2.1/newspaper_tiff_alto_pdf_ebe47259-8f23-4a2d-bf49-55ae1d855393",
    "tests/sip-examples/2.1/newspaper_c44a0b0d-6e2f-4af2-9dab-3a9d447288d0",
    "tests/sip-examples/2.1/subtitles_d3e1a978-3dd8-4b46-9314-d9189a1c94c6",
    "tests/sip-examples/2.1/ftp_sidecar_904c6e86-d36a-4630-897b-bb560ce4b690",
]
unzipped_paths = [
    next(path.iterdir()) for path in sip_paths if str(path) not in excludes
]


@pytest.mark.parametrize("unzipped_path", unzipped_paths)
def test_sip_with_dc_schema_example_parsing(unzipped_path: Path):
    SIP[DCPlusSchema].from_path(unzipped_path, DCPlusSchema)
