import os
from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    session,
    send_file,
    redirect,
    url_for,
    flash,
)

from pricing import calculate_order, parse_items, line_total
from receipt import generate_receipt

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "Set the FLASK_SECRET_KEY environment variable before starting the app."
    )


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    order_text = ""

    if request.method == "POST":
        order_text = request.form.get("items", "")

        try:
            items = parse_items(order_text)

            if not items:
                raise ValueError("Enter at least one order item.")

            result = calculate_order(items)

            for item in items:
                item["line_total"] = line_total(item)

            result["items"] = items

            session["receipt_items"] = [
                {
                    "name": item["name"],
                    "price": str(item["price"]),
                    "qty": item["qty"],
                }
                for item in items
            ]

        except (ValueError, ArithmeticError) as exc:
            error = str(exc)
            session.pop("receipt_items", None)

    return render_template(
        "index.html",
        result=result,
        error=error,
        items_text=order_text,
    )


@app.route("/download-receipt")
def download_receipt():
    saved_items = session.get("receipt_items")

    if not saved_items:
        flash("Please calculate an order before downloading a receipt.")
        return redirect(url_for("index"))

    try:
        items = parse_items(
            "\n".join(
                f"{item['name']}, {item['price']}, {item['qty']}"
                for item in saved_items
            )
        )

        result = calculate_order(items)

        for item in items:
            item["line_total"] = line_total(item)

        result["items"] = items
        receipt_text = generate_receipt(result)

    except (ValueError, ArithmeticError):
        session.pop("receipt_items", None)
        flash("Unable to generate the receipt. Please calculate your order again.")
        return redirect(url_for("index"))

    receipt_file = BytesIO(receipt_text.encode("utf-8"))
    receipt_file.seek(0)

    return send_file(
        receipt_file,
        mimetype="text/plain",
        as_attachment=True,
        download_name="order-receipt.txt",
    )


if __name__ == "__main__":
    app.run(debug=True)
