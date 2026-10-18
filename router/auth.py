from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Annotated

from models import UserModel
from schemas import UserBase
from database import get_db

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/auth/register")
def register(db: DBSession, data: UserBase):
    existing_username = (
        db.query(UserModel).filter(UserModel.username == data.username).first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409, detail="Username already exist! Please try another one."
        )

    existing_email = db.query(UserModel).filter(UserModel.email == data.email).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="This email is already exist!")

    users_data = UserModel(
        username=data.username, email=data.email, hashed_password=data.password
    )

    db.add(users_data)
    db.commit()

    return JSONResponse(
        status_code=201, content={"message": "Successfully registered!"}
    )
