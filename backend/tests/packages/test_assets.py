from random import Random

import pytest
from src.utils import assets


@pytest.mark.parametrize(
    "filename",
    "fontsize",
    [(k, Random().randint(1, 50)) for k in assets.FONT_MAPPING.keys()],
)
def test_font(filename: str, fontsize: int):
    font = assets.font_loader(filename, fontsize)
    assert isinstance(font, assets.image.Ex.ImageFont.FreeTypeFont)
    assert font.size == fontsize


@pytest.mark.parametrize("iconname", list(assets.FONT_MAPPING.keys()))
def test_icon(iconname: str):
    icon = assets.icon_loader(iconname)
    assert isinstance(icon, assets.io.BytesIO)
