from typing import Optional

from fastapi import FastAPI, Depends, HTTPException

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import engine, Base, SessionLocal

from auth import get_current_user, get_user_exception


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1-5")
    complete: bool


@app.get("/")
async def read_all(
    db: Session = Depends(get_db),
):  # always close database, injecting dependency
    """curl -X 'GET' 'http://localhost:8000/' -H 'accept: application/json'"""
    return db.query(models.Todos).all()


@app.get("/todos/user")
async def read_all_by_user(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()


@app.get("/todo/{todo_id}")
async def read_todo(
    todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    print(user)
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    else:
        raise http_exception()


@app.post("/")
async def create_todo(
    todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()  # Model instance
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")
    db.add(todo_model)  # add to database
    db.commit()  # need to commit
    return successful_response(status_code=201)


@app.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    todo: Todo,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo_model = (
        db.query(models.Todos)  # sqlalchemy Query object
        .filter(models.Todos.id == todo_id)  # still sqlalchemy Query object
        .filter(models.Todos.owner_id == user.get("id"))
        .first()  # model instance or None
    )
    if todo_model is None:
        raise http_exception()
    else:
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.complete = todo.complete
        db.add(todo_model)  # basically an update/replace
        db.commit()  # need to commit
        return successful_response(status_code=200)


@app.delete("/{todo_id}")
async def delete_todo(
    todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user is None:
        raise get_user_exception()
    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise http_exception()
    else:
        db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
        db.commit()  # need to commit
        return successful_response(status_code=200)


def successful_response(status_code: int):
    return {"status": status_code, "transaction": "Successful"}


def http_exception():  # regular, not async function
    return HTTPException(status_code=404, detail="Todo not found")
