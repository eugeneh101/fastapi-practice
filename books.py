from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI()  # univcorn books:app --reload

BOOKS = {  # book_name: {title: ..., author: ...}
    "book_1": {"title": "Title One", "author": "Author One"},
    "book_2": {"title": "Title Two", "author": "Author Two"},
    "book_3": {"title": "Title Three", "author": "Author Three"},
    "book_4": {"title": "Title Four", "author": "Author Four"},
    "book_5": {"title": "Title Five", "author": "Author Five"},
}


class DirectionName(str, Enum):
    north = "North"
    south = "South"
    east = "East"
    west = "West"


@app.get("/directions/{direction_name}")
# Swagger doc knows only 4 types of options due to enum
async def get_direction(direction_name: DirectionName):
    if direction_name == DirectionName.north:
        return {"Direction": direction_name, "sub": "Up"}
    elif direction_name == DirectionName.south:
        return {"Direction": direction_name, "sub": "Down"}
    elif direction_name == DirectionName.east:
        return {"Direction": direction_name, "sub": "Right"}
    else:
        return {"Direction": direction_name, "sub": "Left"}


# @app.get("/")
# async def first_api():
#     return {"message": "Hello Eugene!"}
# curl -X 'GET' 'http://127.0.0.1:8000/' -H 'accept: application/json'


@app.get("/")  # http://127.0.0.1:8000/?skip_book=book_1
async def read_all_books(skip_book: Optional[str] = None):  # query parameter
    if skip_book:
        new_books = BOOKS.copy()
        new_books.pop(skip_book)
        return new_books
    else:
        return BOOKS


@app.get("/{book_name}")
async def read_book(book_name: str):
    return BOOKS[book_name]


@app.get("/books/mybook")
async def read_favorite_book():
    return {"book_title": "My favorite book"}


# path parameter uses {}, must be underneath API that follows same kind of path
@app.get("/books/{book_id}")
async def read_book(book_id: int):
    return {"book_title": book_id}


@app.post("/")
async def create_book(book_title: str, book_author: str):
    if len(BOOKS):
        current_book_id = max(int(book.split("_")[-1]) for book in BOOKS)
        BOOKS[f"book_{current_book_id + 1}"] = {
            "title": book_title,
            "author": book_author,
        }
        return BOOKS[f"book_{current_book_id + 1}"]


# book_name is path parameter, but book_title and book_author are query parameters
@app.put("/{book_name}")
async def update_book(book_name: str, book_title: str, book_author: str):
    book_information = {"book_title": book_title, "book_author": book_author}
    BOOKS[book_name] = book_information
    return book_information


@app.delete("/{book_name}")
async def delete_book(book_name: str):
    del BOOKS[book_name]
    return f"Book {book_name} deleted"


@app.get("/assignment/")  # need trailing /
async def read_book_assignment(book_name: str):
    return BOOKS[book_name]


@app.delete("/assignment/")
async def delete_book_assignment(book_name: str):
    del BOOKS[book_name]
    return
