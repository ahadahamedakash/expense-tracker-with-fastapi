from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Annotated

from models import User
from schemas import UserBase
from database import get_db

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]
