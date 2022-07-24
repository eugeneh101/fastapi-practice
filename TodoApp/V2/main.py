from typing import Optional

from fastapi import FastAPI  # , Depends, HTTPException

# from pydantic import BaseModel, Field
# from sqlalchemy.orm import Session

import models
from database import engine  # , Base , SessionLocal
from routers import auth, todos

# from routers.auth import get_current_user, get_user_exception


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todos.router)