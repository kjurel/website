import io

import pydantic
import pytest
from src.utils.editing import image


def test_image_validation():
    img = image.Ex.Image.new("RGB", (100, 100))
    assert image.EXTENSION in ("jpg", "jpeg", "png")
    for k, v in image.SIZE.items():
        num, den = [int(i) for i in k.split(":")]
        assert round(num / den) == round(v[0] / v[1])
    assert isinstance(image.RENDER_SETTINGS, dict)
    with pytest.raises(pydantic.ValidationError):
        image(img=5)
    with pytest.raises(pydantic.ValidationError):
        image(img=img, a=5)
    # get copy
    assert isinstance((T1 := image(img=img)).get_copy, image.Ex.Image.Image)
    assert id(T1.get_copy) != id(img)
    assert image(img=image.Ex.Image.open(io.BytesIO(T1.get_bytes))) == image(img=img)


def test_image_orientation():
    po = image(img=image.Ex.Image.new("RGB", (5, 10)))
    la = image(img=image.Ex.Image.new("RGB", (10, 5)))
    sq = image(img=image.Ex.Image.new("RGB", (5, 5)))
    assert (
        not po.orientation.isLandscape
        and po.orientation.isPotrait
        and not po.orientation.isSquare
    )
    assert (
        la.orientation.isLandscape
        and not la.orientation.isPotrait
        and not la.orientation.isSquare
    )
    assert (
        not sq.orientation.isLandscape
        and not sq.orientation.isPotrait
        and sq.orientation.isSquare
    )


@pytest.mark.parametrize(
    "sample_img_type, sample_img_size, resizing_parameter, resizing_value",
    [
        ("RGB", (100, 100), "height", 200),
        ("RGB", (100, 100), "width", 200),
        ("RGB", (200, 100), "width", 200),
        ("RGB", (200, 100), "height", 200),
        ("RGB", (100, 200), "width", 200),
        ("RGB", (100, 200), "height", 200),
    ],
)
def test_image_resize(
    sample_img_type, sample_img_size, resizing_parameter, resizing_value
):
    im = image.Ex.Image.new(sample_img_type, sample_img_size, "black")
    aspect_ratio = im.width / im.height
    im_new = image(img=im.copy()).resize(resizing_parameter, resizing_value).img
    assert isinstance(im_new, image.Ex.Image.Image)
    assert getattr(im_new, resizing_parameter) == resizing_value
    assert round(im_new.width / im_new.height) == round(aspect_ratio)


# def test_methods_crop(sample_img_type, sample_img_size, resizing_parameter, resizing_value):
#   assert True
