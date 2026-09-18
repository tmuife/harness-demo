"""Shipping fee calculation using the previous policy implementation."""


def calculate_shipping_fee(
    subtotal_cents: int,
    destination: str,
    is_member: bool = False,
) -> int:
    """Return the shipping fee in cents."""
    threshold = 3000 if is_member else 5000

    if subtotal_cents > threshold:
        return 0

    return 800
