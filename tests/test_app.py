from app import app


def setup_test_app():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    return app.test_client()


def test_homepage_loads():
    client = setup_test_app()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Pricing Service" in response.data


def test_valid_order_submission():
    client = setup_test_app()

    response = client.post(
        "/",
        data={"items": "Notebook, 10.00, 2"},
    )

    assert response.status_code == 200
    assert b"Order summary" in response.data
    assert b"20.00" in response.data


def test_invalid_order_submission():
    client = setup_test_app()

    response = client.post(
        "/",
        data={"items": "Notebook, invalid"},
    )

    assert response.status_code == 200
    assert b"Each line must contain a name, price, and quantity." in response.data


def test_receipt_download_after_valid_order():
    client = setup_test_app()

    client.post(
        "/",
        data={"items": "Notebook, 10.00, 2"},
    )

    response = client.get("/download-receipt")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert response.headers["Content-Disposition"].startswith("attachment;")
    assert "order-receipt.txt" in response.headers["Content-Disposition"]


def test_receipt_contains_correct_items_and_totals():
    client = setup_test_app()

    client.post(
        "/",
        data={
            "items": (
                "Laptop, 80, 1\n"
                "Mouse, 15, 2\n"
                "Keyboard, 25, 1"
            )
        },
    )

    response = client.get("/download-receipt")
    receipt = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Laptop | $80.00 x 1 = $80.00" in receipt
    assert "Mouse | $15.00 x 2 = $30.00" in receipt
    assert "Keyboard | $25.00 x 1 = $25.00" in receipt
    assert "Subtotal: $135.00" in receipt
    assert "Discount: -$13.50" in receipt
    assert "TOTAL:    $121.50" in receipt


def test_receipt_download_without_order_redirects():
    client = setup_test_app()

    response = client.get("/download-receipt")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_invalid_order_clears_previous_receipt():
    client = setup_test_app()

    client.post(
        "/",
        data={"items": "Notebook, 10.00, 2"},
    )

    invalid_response = client.post(
        "/",
        data={"items": "Notebook, invalid"},
    )

    assert invalid_response.status_code == 200

    download_response = client.get("/download-receipt")

    assert download_response.status_code == 302
    assert download_response.headers["Location"].endswith("/")
