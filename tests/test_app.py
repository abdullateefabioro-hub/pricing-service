from app import app


def test_homepage_loads():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Pricing Service" in response.data


def test_valid_order_submission():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/",
        data={"items": "Notebook, 10.00, 2"},
    )

    assert response.status_code == 200
    assert b"Order summary" in response.data
    assert b"20.00" in response.data


def test_invalid_order_submission():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.post(
        "/",
        data={"items": "Notebook, invalid"},
    )

    assert response.status_code == 200
    assert b"Each line must contain a name, price, and quantity." in response.data
