"""Test to verify pytest configuration is working."""


def test_pytest_works():
    """Basic test to verify pytest is configured correctly."""
    assert True


def test_imports():
    """Test that we can import from our src directory."""
    from src.lib.types import Point, Rect, ElementType

    p = Point(10, 20)
    assert p.x == 10
    assert p.y == 20

    r = Rect(0, 0, 100, 100)
    assert r.width == 100
    assert r.height == 100

    assert ElementType.CARD.value == "card"
