import sys

sys.path.append("..")

from datetime import datetime, timedelta
from typing import Optional, Union


from starlette.responses import RedirectResponse
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response,
    Request,
    status,  # has a bunch of status codes
)
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine


SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)  # create databases
# app = FastAPI()
router = APIRouter(
    prefix="/auth",  # prefix to url
    tags=["auth"],  # puts in separate group in Swagger docs
    responses={401: {"user": "Not authorized"}},
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):  # does this really need async?
        form = await self.request.form()  # form is very dict-like
        self.username = form.get("email")
        self.password = form.get("password")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db) -> Union[models.Users, bool]:
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
) -> str:
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode["exp"] = expire
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request) -> Optional[dict]:
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # actually checks `exp`
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if (username is None) or (user_id is None):
            # raise HTTPException(status_code=404, detail="User not found")
            # raise get_user_exception()
            # return None
            logout(request=request)
        return {"username": username, "id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=404, details="Not found")


@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),  # what does Depends() by itself do?
    db: Session = Depends(get_db),
) -> bool:
    user = authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    if not user:
        # raise HTTPException(status_code=404, detail="User not found")
        return False  # raise token_exception()
    # return "User Validated"
    token_expires = timedelta(minutes=60)
    token = create_access_token(
        username=user.username, user_id=user.id, expires_delta=token_expires
    )
    response.set_cookie(key="access_token", value=token, httponly=True)  # mutates state
    return True  # {"token": token}


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}  # apparently "request" is a required key
    )


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request=request)
        await form.create_oauth_form()  # does this really need await?
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )  # calls endpoint function directly
        if not validate_user_cookie:  # unsuccessful goes back to the same page
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response  # successful goes to /todo
    except HTTPException:  # what is this excepting?
        msg = "Unknown Error"
        return templates.TemplateResponse(  # unsuccessful goes back to the same page
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg}
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    validation1 = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()
    if (
        (password != password2)
        or (validation1 is not None)
        or (validation2 is not None)
    ):
        msg = "Invalid registration request"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    user_model.hashed_password = get_password_hash(password=password)
    user_model.is_active = True
    db.add(user_model)
    db.commit()
    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
