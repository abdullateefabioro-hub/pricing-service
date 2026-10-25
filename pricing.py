from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")
DISCOUNT_RATE = Decimal("0.10")
DISCOUNT_THRESHOLD = Decimal("100.00")


def money(value):
    """Convert a value to a finite monetary amount rounded to cents."""
    try:
        amount = Decimal(str(value))

        if not amount.is_finite():
            raise ValueError("Price must be a valid number.")

        return amount.quantize(CENT, rounding=ROUND_HALF_UP)

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Price must be a valid number.") from None


def line_total(item):
    """Calculate the total price for one order line."""
    price = money(item["price"])

    try:
        quantity_decimal = Decimal(str(item["qty"]))

        if (
            not quantity_decimal.is_finite()
            or quantity_decimal != quantity_decimal.to_integral_value()
        ):
            raise ValueError("Quantity must be a whole number.")

        quantity = int(quantity_decimal)

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Quantity must be a whole number.") from None

    if price < 0:
        raise ValueError("Price must be non-negative.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

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
            raise ValueError(
                "Each line must contain a name, price, and quantity."
            )

        name, price, quantity = parts

        if not name:
            raise ValueError("Item name cannot be empty.")

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a whole number.") from None

        items.append({
            "name": name,
            "price": price,
            "qty": quantity,
        })

    return items
