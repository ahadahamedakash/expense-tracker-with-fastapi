from datetime import date
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class TransactionBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str = Field(min_length=1, max_length=100)
    date: date


class UpdateTransaction(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    type: Literal["income", "expense"] | None = None
    date: date | None = None
