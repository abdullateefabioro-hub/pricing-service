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

def test_zero_price_item():
    items = [{"name": "Free sample", "price": "0.00", "qty": 1}]
    result = calculate_order(items)
    assert result["subtotal"] == Decimal("0.00")
    assert result["total"] == Decimal("0.00")


def test_quantity_greater_than_one():
    items = [{"name": "Notebook", "price": "4.50", "qty": 3}]
    result = calculate_order(items)
    assert result["subtotal"] == Decimal("13.50")


def test_discount_not_applied_below_threshold():
    items = [{"name": "Item", "price": "99.99", "qty": 1}]
    result = calculate_order(items)
    assert result["discount"] == Decimal("0.00")
    assert result["total"] == Decimal("99.99")


def test_discount_applied_above_threshold():
    items = [{"name": "Item", "price": "120.00", "qty": 1}]
    result = calculate_order(items)
    assert result["discount"] == Decimal("12.00")
    assert result["total"] == Decimal("108.00")


def test_negative_price_is_rejected():
    items = [{"name": "Item", "price": "-5.00", "qty": 1}]

    import pytest

    with pytest.raises(ValueError):
        calculate_order(items)


def test_zero_quantity_is_rejected():
    items = [{"name": "Item", "price": "5.00", "qty": 0}]

    import pytest

    with pytest.raises(ValueError):
        calculate_order(items)


def test_negative_quantity_is_rejected():
    items = [{"name": "Item", "price": "5.00", "qty": -2}]

    import pytest

    with pytest.raises(ValueError):
        calculate_order(items)
