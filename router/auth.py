from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from sqlalchemy.orm import Session

from jose import jwt

from pydantic import BaseModel

from passlib.context import CryptContext

from typing import Annotated
from datetime import timedelta, datetime, timezone

from models import UserModel
from schemas import UserBase
from database import get_db

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "f947ed70fb914dff44e23f83f3abfbddd1ed14316d29126d9e4ed484a37e70c1"
ALGORITHM = "HS256"

DBSession = Annotated[Session, Depends(get_db)]


def authenticate_user(username, password, db):
    current_user = db.query(UserModel).filter(UserModel.username == username).first()

    print(current_user)

    if current_user is None:
        return None

    if bcrypt_context.verify(password, current_user.hashed_password):
        return current_user

    return None


def generate_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}

    expires = datetime.now(timezone.utc) + expires_delta

    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found!")

        return {"username": username, "id": user_id}
    except:
        raise HTTPException(status_code=404, detail="User not found!")


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
        username=data.username,
        email=data.email,
        hashed_password=bcrypt_context.hash(data.password),
    )

    db.add(users_data)
    db.commit()

    return JSONResponse(
        status_code=201, content={"message": "Successfully registered!"}
    )


@router.post("/auth/login")
def login(db: DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        return JSONResponse(
            status_code=401, content={"message": "You are unauthorized!"}
        )

    token = generate_access_token(user.username, user.id, timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer"}
