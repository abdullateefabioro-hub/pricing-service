import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "orders.db"


def get_connection():
    """Open a connection to the order database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create the order tables if they do not already exist."""
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                subtotal TEXT NOT NULL,
                discount TEXT NOT NULL,
                total TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                line_total TEXT NOT NULL,
                FOREIGN KEY (order_id)
                    REFERENCES orders (id)
                    ON DELETE CASCADE
            );
            """
        )


def save_order(result, order_number=None):
    """Save an order and its items, returning its unique order number."""
    initialize_database()

    if order_number is None:
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        order_number = f"ORD-{date_part}-{secrets.token_hex(4).upper()}"

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO orders (
                order_number, subtotal, discount, total, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                order_number,
                str(result["subtotal"]),
                str(result["discount"]),
                str(result["total"]),
                created_at,
            ),
        )

        order_id = cursor.lastrowid

        for item in result["items"]:
            connection.execute(
                """
                INSERT INTO order_items (
                    order_id, name, price, quantity, line_total
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["name"],
                    str(item["price"]),
                    int(item["qty"]),
                    str(item["line_total"]),
                ),
            )

    return order_number


def get_order(order_number):
    """Retrieve a saved order and its items by order number."""
    initialize_database()

    with get_connection() as connection:
        order = connection.execute(
            "SELECT * FROM orders WHERE order_number = ?",
            (order_number,),
        ).fetchone()

        if order is None:
            return None

        rows = connection.execute(
            """
            SELECT name, price, quantity, line_total
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
            """,
            (order["id"],),
        ).fetchall()

    return {
        "order_number": order["order_number"],
        "created_at": order["created_at"],
        "subtotal": order["subtotal"],
        "discount": order["discount"],
        "total": order["total"],
        "items": [
            {
                "name": item["name"],
                "price": item["price"],
                "qty": item["quantity"],
                "line_total": item["line_total"],
            }
            for item in rows
        ],
    }
