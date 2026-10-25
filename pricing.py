from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
DISCOUNT_RATE = Decimal("0.10")
DISCOUNT_THRESHOLD = Decimal("100.00")


def money(value):
    """Convert a value to a monetary amount rounded to cents."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(item):
    """Calculate the total price for one order line."""
    price = money(item["price"])
    quantity = int(item["qty"])

    if price < 0 or quantity <= 0:
        raise ValueError("Price must be non-negative and quantity must be positive.")

    return price * quantity


def calculate_subtotal(items):
    """Calculate the subtotal before discounts."""
    return sum(
        (line_total(item) for item in items),
        Decimal("0.00"),
    )


def calculate_order(items):
    """Calculate an order subtotal, discount, and final total."""
    subtotal = calculate_subtotal(items)
    discount = Decimal("0.00")

    if subtotal > DISCOUNT_THRESHOLD:
        discount = money(subtotal * DISCOUNT_RATE)

    return {
        "subtotal": subtotal,
        "discount": discount,
        "total": subtotal - discount,
    }


def parse_items(text):
    """Parse order lines in the format: name, price, quantity."""
    items = []

    for raw_line in text.strip().splitlines():
        if not raw_line.strip():
            continue

        parts = [part.strip() for part in raw_line.split(",")]

        if len(parts) != 3:
            raise ValueError("Each line must contain a name, price, and quantity.")

        name, price, quantity = parts

        items.append({
            "name": name,
            "price": price,
            "qty": int(quantity),
        })

    return items