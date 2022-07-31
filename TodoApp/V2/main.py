from fastapi import FastAPI, Depends  # , HTTPException

# from pydantic import BaseModel, Field
# from sqlalchemy.orm import Session

import models
from database import engine  # , Base , SessionLocal
from company import companyapis, dependencies
from routers import auth, todos, users

# from routers.auth import get_current_user, get_user_exception


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(
    companyapis.router,
    prefix="/companyapis",  # can put arguments here instead of companyapis.py
    tags=["companyapis"],
    dependencies=[
        Depends(dependencies.get_token_header)
    ],  # I assume this adds dependencies to all endpoints
    responses={418: {"description": "Internal use only"}},
)
app.include_router(users.router)
