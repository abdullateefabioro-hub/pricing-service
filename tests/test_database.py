import sqlite3

import pytest

import database
from database import get_order, initialize_database, save_order
from pricing import calculate_order, line_total, parse_items


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Use a separate temporary database for each test."""
    test_db_path = tmp_path / "test_orders.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db_path)
    initialize_database()
    return test_db_path


def make_order(text):
    """Build an order using the application's existing pricing functions."""
    items = parse_items(text)
    result = calculate_order(items)

    for item in items:
        item["line_total"] = line_total(item)

    result["items"] = items
    return result


def test_save_and_retrieve_order(test_database):
    result = make_order("Keyboard, 75.00, 1\nMouse, 30.00, 1")

    order_number = save_order(result)
    saved_order = get_order(order_number)

    assert saved_order is not None
    assert saved_order["order_number"] == order_number
    assert saved_order["subtotal"] == "105.00"
    assert saved_order["discount"] == "10.50"
    assert saved_order["total"] == "94.50"
    assert len(saved_order["items"]) == 2
    assert saved_order["items"][0]["name"] == "Keyboard"
    assert saved_order["items"][1]["name"] == "Mouse"


def test_missing_order_returns_none(test_database):
    assert get_order("ORD-DOES-NOT-EXIST") is None


def test_multiple_orders_have_unique_numbers(test_database):
    result = make_order("Notebook, 5.00, 2")

    first_number = save_order(result)
    second_number = save_order(result)

    assert first_number != second_number
    assert get_order(first_number) is not None
    assert get_order(second_number) is not None


def test_duplicate_order_number_does_not_leave_partial_order(test_database):
    result = make_order("Notebook, 5.00, 2")

    save_order(result, order_number="ORD-TEST-001")

    with pytest.raises(sqlite3.IntegrityError):
        save_order(result, order_number="ORD-TEST-001")

    with sqlite3.connect(test_database) as connection:
        order_count = connection.execute(
            "SELECT COUNT(*) FROM orders WHERE order_number = ?",
            ("ORD-TEST-001",),
        ).fetchone()[0]

        item_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM order_items
            WHERE order_id = (
                SELECT id FROM orders WHERE order_number = ?
            )
            """,
            ("ORD-TEST-001",),
        ).fetchone()[0]

    assert order_count == 1
    assert item_count == 1
