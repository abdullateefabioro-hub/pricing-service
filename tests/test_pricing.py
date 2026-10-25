from decimal import Decimal

import pytest

from pricing import calculate_order, calculate_subtotal, parse_items


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
    with pytest.raises(ValueError):
        calculate_order(items)


def test_zero_quantity_is_rejected():
    items = [{"name": "Item", "price": "5.00", "qty": 0}]
    with pytest.raises(ValueError):
        calculate_order(items)


def test_negative_quantity_is_rejected():
    items = [{"name": "Item", "price": "5.00", "qty": -2}]
    with pytest.raises(ValueError):
        calculate_order(items)


def test_parse_single_item():
    items = parse_items("Notebook, 4.50, 2")
    assert items == [
        {"name": "Notebook", "price": "4.50", "qty": 2}
    ]


def test_parse_multiple_items():
    text = "Notebook, 4.50, 2\nPen, 1.25, 3"
    items = parse_items(text)
    assert len(items) == 2
    assert items[0]["name"] == "Notebook"
    assert items[1]["name"] == "Pen"


def test_parse_invalid_line_is_rejected():
    with pytest.raises(ValueError):
        parse_items("Notebook, 4.50")


def test_invalid_price_is_rejected():
    items = [{"name": "Notebook", "price": "abc", "qty": 2}]
    with pytest.raises(ValueError, match="Price must be a valid number."):
        calculate_order(items)


def test_invalid_quantity_text_is_rejected():
    with pytest.raises(
        ValueError,
        match="Quantity must be a whole number.",
    ):
        parse_items("Notebook, 10.00, two")


def test_empty_item_name_is_rejected():
    with pytest.raises(ValueError, match="Item name cannot be empty."):
        parse_items(", 10.00, 2")


def test_empty_order_text_returns_no_items():
    assert parse_items("") == []


def test_nan_price_is_rejected():
    items = [{"name": "Item", "price": "NaN", "qty": 1}]
    with pytest.raises(
        ValueError,
        match="Price must be a valid number.",
    ):
        calculate_order(items)


def test_infinite_price_is_rejected():
    items = [{"name": "Item", "price": "Infinity", "qty": 1}]
    with pytest.raises(
        ValueError,
        match="Price must be a valid number.",
    ):
        calculate_order(items)


def test_fractional_quantity_is_rejected():
    items = [{"name": "Item", "price": "5.00", "qty": 2.5}]
    with pytest.raises(
        ValueError,
        match="Quantity must be a whole number.",
    ):
        calculate_order(items)
