from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Annotated

from models import UserModel, TransactionModel
from schemas import UserBase, TransactionBase
from database import get_db
from router.auth import get_current_user

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]
UserSession = Annotated[dict, Depends(get_current_user)]


@router.get("/transactions")
def get_transactions(user: UserSession, db: DBSession):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    return (
        db.query(TransactionModel)
        .filter(TransactionModel.owner_id == user.get("id"))
        .all()
    )


@router.post("/transactions")
def add_transaction(user: UserSession, db: DBSession, data: TransactionBase):
    if user is None:
        raise HTTPException(status_code=401, detail="You are unauthorized!")

    current_data = TransactionModel(**data.model_dump(), owner_id=user.get("id"))

    db.add(current_data)
    db.commit()
    db.refresh()

    return JSONResponse(status_code=201, content={"message": "Added Successfully!"})
