import sys

sys.path.append("..")  ### need to make less janky

from typing import Generator

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import models
from database import SessionLocal, engine


router = APIRouter(
    prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}}
)
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get(
    "/", response_class=HTMLResponse
)  # what does the response_class do here? it doesn't appear necessary for rendering
async def read_all_by_user(request: Request):  # what does request do?
    return templates.TemplateResponse(  # use template
        "home.html", {"request": request}
    )  # this your context


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request):
    return templates.TemplateResponse("edit-todo.html", {"request": request})
