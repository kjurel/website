"""Hello unit test module."""

from backend_fastapipy.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello backend-fastapipy"
