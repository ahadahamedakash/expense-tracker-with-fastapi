from fastapi import Depends, HTTPException, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Annotated, Literal

from models import UserModel, TransactionModel
from schemas import UserBase, TransactionBase, UpdateTransaction
from database import get_db
from router.auth import get_current_user

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]
UserSession = Annotated[dict, Depends(get_current_user)]


@router.get("/transactions")
def get_transactions(user: UserSession, db: DBSession):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    transactions = (
        db.query(TransactionModel)
        .filter(TransactionModel.owner_id == user.get("id"))
        .all()
    )

    if not transactions:
        raise HTTPException(status_code=404, detail="No transaction found!")

    return transactions


@router.post("/transactions", status_code=201)
def add_transaction(user: UserSession, db: DBSession, data: TransactionBase):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    current_data = TransactionModel(**data.model_dump(), owner_id=user.get("id"))

    db.add(current_data)
    db.commit()
    db.refresh(current_data)

    # return JSONResponse(status_code=201, content={"message": "Added Successfully!"})

    return current_data


@router.get("/transactions/filter")  # type category minimum_amount maximum_amount
def get_filtered_transactions(
    user: UserSession,
    db: DBSession,
    type: Literal["income", "expense"] | None = None,
    category: str | None = None,
    minimum_amount: float | None = Query(default=None, ge=0),
    maximum_amount: float | None = Query(default=None, ge=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    query = db.query(TransactionModel).filter(
        TransactionModel.owner_id == user.get("id")
    )

    if type is not None:
        query = query.filter(TransactionModel.type == type)

    if category is not None:
        query = query.filter(TransactionModel.category == category)

    if minimum_amount is not None:
        query = query.filter(TransactionModel.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(TransactionModel.amount <= maximum_amount)

    return query.all()


@router.get("/transactions/{transaction_id}")
def get_transaction_by_id(transaction_id: int, user: UserSession, db: DBSession):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.owner_id == user.get("id"),
        )
        .first()
    )

    return transaction


@router.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int, data: UpdateTransaction, db: DBSession, user: UserSession
):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.owner_id == user.get("id"),
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found!")

    update_data = data.model_dump(exclude_unset=True)

    for key, val in update_data.items():
        setattr(transaction, key, val)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, user: UserSession, db: DBSession):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.owner_id == user.get("id"),
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found!")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully!"}
