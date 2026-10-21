from fastapi import status
from test.test_main import client

from datetime import date

from main import app

from database import SessionLocal
from models import TransactionModel
from router.auth import get_current_user


def override_user():
    return {
        "id": 1,
        "username": "testuser",
    }


def create_transaction():
    db = SessionLocal()

    try:
        db.query(TransactionModel).filter(TransactionModel.id == 100).delete()

        db.commit()

        transaction = TransactionModel(
            id=100,
            title="Test Title",
            amount=500,
            category="category",
            type="income",
            date=date(2026, 10, 10),
            owner_id=1,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    finally:
        db.close()


app.dependency_overrides[get_current_user] = override_user


def test_read_transaction():
    response = client.get("/transactions")

    assert response.status_code == status.HTTP_200_OK


def test_create_transaction():
    db = SessionLocal()

    try:
        db.query(TransactionModel).filter(TransactionModel.id == 100).delete()
        db.commit()
    finally:
        db.close()

    request_data = {
        "id": 100,
        "title": "Test Title",
        "amount": 500,
        "category": "category",
        "type": "income",
        "date": "2026-10-10",
    }

    response = client.post("/transactions", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_filter_transaction():
    create_transaction()

    response = client.get(
        "/transactions/filter",
        params={
            "type": "income",
            "category": "category",
            "minimum_amount": 10,
            "maximum_amount": 1000,
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_read_transaction_by_id():
    create_transaction()

    response = client.get("/transactions/100")

    assert response.status_code == status.HTTP_200_OK


def test_update_transaction():
    create_transaction()

    request_data = {"title": "Updated Title", "amount": 700, "category": "update_test"}

    response = client.put("/transactions/100", json=request_data)

    assert response.status_code == status.HTTP_200_OK


def test_delete_transaction():
    create_transaction()

    response = client.delete("/transactions/100")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Transaction deleted successfully!"}
