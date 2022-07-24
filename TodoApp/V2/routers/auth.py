import sys
sys.path.append("..")

from datetime import datetime, timedelta
from typing import Optional

from fastapi import (
    #    FastAPI,
    Depends,
    HTTPException,
    status,  # has a bunch of status codes
    APIRouter,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)  # create databases

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
# app = FastAPI()
router = APIRouter()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if not verify_password(
        plain_password=password, hashed_password=user.hashed_password
    ):
        return False
    return user


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode["exp"] = expire
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # actually checks `exp`
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if (username is None) or (user_id is None):
            # raise HTTPException(status_code=404, detail="User not found")
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError as e:
        # raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=404, detail=str(e))
        raise get_user_exception()


@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = (
        create_user.email
    )  # if nullable is not set to False, then can be NULL
    create_user_model.username = (
        create_user.username
    )  # which means that you mistype the attribute on the instance
    create_user_model.first_name = (
        create_user.first_name
    )  # then that attribute is not saved to db on .commit()
    create_user_model.last_name = create_user.last_name  # and resolves to NULL
    create_user_model.hashed_password = get_password_hash(password=create_user.password)
    create_user_model.is_active = True
    db.add(create_user_model)
    db.commit()
    # return str(
    #     vars(create_user_model)
    # )  # once model is committed, it seems the data is removed from the instance
    return "User created!"


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),  # what does Depends() by itself do?
):
    user = authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    if not user:
        # raise HTTPException(status_code=404, detail="User not found")
        raise token_exception()
    # return "User Validated"
    token_expires = timedelta(minutes=20)
    token = create_access_token(
        username=user.username, user_id=user.id, expires_delta=token_expires
    )
    return {"token": token}


# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
