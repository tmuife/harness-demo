import inspect

from shipping import calculate_shipping_fee


def test_domestic_regular_below_threshold() -> None:
    assert calculate_shipping_fee(4999, "domestic") == 800


def test_domestic_regular_at_threshold() -> None:
    assert calculate_shipping_fee(5000, "domestic") == 0


def test_domestic_member_below_threshold() -> None:
    assert calculate_shipping_fee(2999, "domestic", True) == 800


def test_domestic_member_at_threshold() -> None:
    assert calculate_shipping_fee(3000, "domestic", True) == 0


def test_international_order_is_never_free() -> None:
    assert calculate_shipping_fee(10_000, "international") == 2000


def test_public_signature_is_preserved() -> None:
    signature = inspect.signature(calculate_shipping_fee)
    assert list(signature.parameters) == ["subtotal_cents", "destination", "is_member"]
    assert signature.parameters["is_member"].default is False
