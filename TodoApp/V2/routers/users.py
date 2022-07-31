import sys
from urllib.parse import uses_fragment

sys.path.append("..")
from typing import Generator, List, Union

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

import models
from .auth import get_current_user, get_password_hash, get_user_exception
from database import engine, SessionLocal


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},  # what does responses do?
)
models.Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def get_all_users(db: Session = Depends(get_db)) -> List[str]:
    users = db.query(models.Users).all()
    return users
    # return [user.username for user in users]


@router.get("/user/{user_id}")
async def get_user_by_path(
    user_id: int, db: Session = Depends(get_db)
) -> Union[models.Users, str]:
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user is not None:
        return user
    else:
        return f"Invalid user id {user_id}"


@router.get("/user/")
async def get_user_by_query(
    user_id: int, db: Session = Depends(get_db)
) -> Union[models.Users, str]:
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user is not None:
        return user
    else:
        return f"Invalid user id {user_id}"


from pydantic import BaseModel


# class Password(BaseModel):
#     password: str


# @router.put("/password/")  ### post or put? put because modifying existing resource
# async def update_password(
#     # token: str = Depends(oauth2_bearer),
#     password: Password,
#     user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> str:
#     if user is None:
#         raise get_user_exception()
#     else:
#         user = db.query(models.Users).filter(models.Users.id == user["id"]).first()
#         user.hashed_password = get_password_hash(password=password.password)
#         db.add(user)
#         db.commit()
#         return "Password successfully updated"


from .auth import authenticate_user, verify_password


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


# @router.put("/password/")
# async def update_password(
#     user_verification: UserVerification, db: Session = Depends(get_db),
# ) -> str:
#     authenticated_user = authenticate_user(
#         username=user_verification.username, password=user_verification.password, db=db
#     )
#     if not authenticated_user:
#         raise get_user_exception()
#     else:
#         authenticated_user.hashed_password = get_password_hash(
#             password=user_verification.new_password
#         )
#         db.add(authenticated_user)
#         db.commit()
#         return "Password successfully updated"


@router.put("/password/")
async def update_password(
    user_verification: UserVerification,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    if user is None:
        raise get_user_exception()
    else:
        user_model = (
            db.query(models.Users).filter(models.Users.id == user["id"]).first()
        )
        if (
            user_model is not None
            and (user_verification.username == user["username"])
            and verify_password(
                plain_password=user_verification.password,  # seems to automatically raise exception
                hashed_password=user_model.hashed_password,  # so don't need `else` block
            )
        ):
            user_model.hashed_password = get_password_hash(
                password=user_verification.new_password
            )
            db.add(user_model)
            db.commit()
            return "Password successfully updated"
        else:
            raise get_user_exception()  # username is not matching


@router.delete("/user/")
def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_model = (
        db.query(models.Users).filter(models.Users.username == user["username"]).first()
    )
    if user_model is None:
        return f"User {user['username']} does not exist"
    else:
        db.query(models.Users).filter(
            models.Users.username == user["username"]
        ).delete()
        db.commit()
        # probably also want do delete all the tasks
        return f"User {user['username']} deleted"


# Enhance users.py to be able to get a single user by a path parameter: DONE
# Enhance users.py to be able to get a single user by a query parameter: DONE
# Enhance users.py to be able to modify their current user's password, if passed by authentication: DONE
# Enhance users.py to be able to delete their own user.
