from flask import Flask, render_template, request

from pricing import calculate_order, parse_items

app = Flask(__name__)


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

        except (ValueError, ArithmeticError) as exc:
            error = str(exc)

    return render_template(
        "index.html",
        result=result,
        error=error,
        items_text=order_text,
    )


if __name__ == "__main__":
    app.run(debug=True)