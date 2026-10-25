from decimal import Decimal

from pricing import calculate_order, calculate_subtotal


def test_subtotal_multiple_items():
    items = [
        {"name": "Pen", "price": "2.50", "qty": 4},
        {"name": "Book", "price": "12.00", "qty": 1},
    ]

    assert calculate_subtotal(items) == Decimal("22.00")


def test_no_discount_at_100_dollars():
    items = [{"name": "Item", "price": "50.00", "qty": 2}]

    order = calculate_order(items)

    assert order["subtotal"] == Decimal("100.00")
    assert order["discount"] == Decimal("0.00")
    assert order["total"] == Decimal("100.00")


def test_discount_above_100_dollars():
    items = [{"name": "Item", "price": "60.00", "qty": 2}]

    order = calculate_order(items)

    assert order["subtotal"] == Decimal("120.00")
    assert order["discount"] == Decimal("12.00")
    assert order["total"] == Decimal("108.00")