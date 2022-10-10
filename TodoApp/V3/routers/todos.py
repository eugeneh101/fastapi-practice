import sys

sys.path.append("..")  ### need to make less janky

from typing import Generator


from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

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
async def read_all_by_user(
    request: Request, db: Session = Depends(get_db)
):  # what does request do?
    todos = db.query(models.Todos).filter(models.Todos.owner_id == 1).all()
    return templates.TemplateResponse(  # use template
        "home.html", {"request": request, "todos": todos}
    )  # this your context


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1
    db.add(todo_model)
    db.commit()
    return RedirectResponse(
        url="/todos", status_code=status.HTTP_302_FOUND
    )  # will redirect as a GET /todos


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request):
    return templates.TemplateResponse("edit-todo.html", {"request": request})
