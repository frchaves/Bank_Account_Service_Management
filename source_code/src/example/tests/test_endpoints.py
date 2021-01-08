import pytest
import json
from ..app import create_app


@pytest.fixture
def app():
    app = create_app()

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_create(client):

    account_examples = {
        "account_1": {
            "name": "Johannes",
            "IBAN": "DE12 5001 0517 0648 4898 90",
            "balance": 1213.3,
            "currency": "USD"
        },
        "account_2":{
            "name": "John",
            "IBAN": "DE89 3704 0044 0532 0130 00",
            "balance": 250.45,
            "currency": "EUR"
        },
        "account_3":{
            "name": "Peter",
            "IBAN": "DE91 1000 0000 0123 4567 89",
            "balance": 213.3,
            "currency": "USD"
        }
    }

    dataj = json.dumps(account_examples)
    response = client.post("/Accounts/account/add", data=dataj, content_type='application/json')

    assert response.status_code == 200

def test_read_all_accounts(client):
    response = client.get('/Accounts/accounts')

    assert response.status_code == 200


def test_read_one(client):

    response = client.get('Accounts/account/DE12 5001 0517 0648 4898 90')
    assert response.status_code == 200


def test_update(client):
    data = {
        "name": "Franz",
        "IBAN": "DE12 5001 0517 0648 4898 90",
        "balance": 250,
        "currency": "USD"
    }
    datajson = json.dumps(data)
    response = client.patch("Accounts/account/edit/DE12 5001 0517 0648 4898 90", data=datajson, content_type='application/json')
    assert response.status_code == 200


def test_delete(client):
    response = client.delete('Accounts/account/remove/DE12 5001 0517 0648 4898 90')
    assert response.status_code == 200


def test_create_transaction(client):
    transaction = {
            "from_IBAN": "DE91 1000 0000 0123 4567 89",
            "to_IBAN": "DE89 3704 0044 0532 0130 00",
            "account_id": 2,
            "amount": 30.5,
            "send_currency": "USD",
            "receive_currency": "USD",
    }
    datajson = json.dumps(transaction)
    response = client.post("/Accounts/transactions/add", data=datajson, content_type='application/json')
    assert response.status_code == 200


def test_read_all_transactions(client):
    response = client.get('/Accounts/transactions')
    assert response.status_code == 200