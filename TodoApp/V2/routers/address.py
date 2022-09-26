import sys

sys.path.append("..")

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from .auth import get_current_user, get_user_exception
from database import engine, SessionLocal


router = APIRouter(
    prefix="/address", tags=["address"], responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Address(BaseModel):
    address1: str
    address2: str
    city: str
    state: str
    country: str
    postalcode: str
    apt_num: Optional[int]


@router.post("/")
async def create_address(
    address: Address,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user is None:
        raise get_user_exception()
    address_model = models.Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num
    db.add(address_model)
    db.flush()  # instead of commit(), flush() gets staged for commit and returns id (any column(s) that database creates automatically)
    user_model = (
        db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    )
    user_model.address_id = address_model.id
    db.add(user_model)
    db.commit()

