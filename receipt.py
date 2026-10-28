from datetime import datetime


def generate_receipt(result, order_number=None):
    """Generate a readable text receipt for a completed order."""
    lines = [
        "========================================",
        "             ORDER RECEIPT",
        "========================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if order_number:
        lines.append(f"Order Number: {order_number}")

    lines.extend([
        "",
        "ITEMS",
        "----------------------------------------",
    ])

    for item in result["items"]:
        name = item["name"]
        price = float(item["price"])
        quantity = item["qty"]
        total = float(item["line_total"])

        lines.append(
            f"{name} | ${price:.2f} x {quantity} = ${total:.2f}"
        )

    lines.extend([
        "",
        "----------------------------------------",
        f"Subtotal: ${float(result['subtotal']):.2f}",
        f"Discount: -${float(result['discount']):.2f}",
        f"TOTAL:    ${float(result['total']):.2f}",
        "========================================",
        "          Thank you for your order!",
        "========================================",
    ])

    return "\n".join(lines) + "\n"
