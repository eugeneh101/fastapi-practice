from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class Book(BaseModel):  # like typed dataclass
    """Appears similar to Flask resource. Look at the Swagger docs and see
    the Schema to know what the fields have to be."""

    id: UUID
    title: str = Field(min_length=1)  # simple validation
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        title="Description of the book", min_length=1, max_length=100
    )  # don't have to set it to None and in Swagger
    # can delete the field and no longer required in the Swagger schema
    rating: int = Field(gt=-1, lt=101)  # will truncate a float

    class Config:
        """Predefined body for Swagger"""

        schema_extra = {
            "example": {
                "id": "a96dbb9b-a650-475b-b899-bb4dac1c0466",
                "title": "Computer Science Pro",
                "author": "Coding with Eugene",
                "description": "A very nice description of a book",
                "rating": 75,
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)  # simple validation
    author: str
    description: Optional[str] = Field(
        default=None,  # set default value
        title="description of the book",
        min_length=1,
        max_length=100,
    )


BOOKS = []
app = FastAPI()


def raise_item_cannot_be_found_exception():  # regular function, not async
    raise HTTPException(
        status_code=404,
        detail="Book not found",
        headers={"X-Header-Error": "nothing to be seen at the UUID"},
    )


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(  # does this have to be async?
    request: Request, exception: NegativeNumberException
):
    """Global exception handling. Write once, use anywhere. DRY, reduce boilerplate code"""
    return JSONResponse(
        status_code=418,
        content={
            "message": (
                f"Hey, why do you want {exception.books_to_return} books? "
                "You need to read more!"
            )
        },
    )


# @app.post("/books/login")
# async def book_login(
#     username: str = Form(), password: str = Form()
# ):  # request body, not path or query parameters; Content type is form-urlencoded
#     """curl -X 'POST' 'http://127.0.0.1:8000/books/login' -H 'accept: application/json'
#     -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=user&password=pass'
#     """
#     return {"username": username, "password": password}


@app.post("/books/login")
async def book_login(
    book_id: int,
    username: str = Header(default=None),
    password: str = Header(default=None),
):
    """curl -X 'POST' 'http://127.0.0.1:8000/books/login?book_id=2' -H 'accept: application/json'
    -H 'username: FastAPIUser' -H 'password: testpass1234!' -d ''
    """
    if username == "FastAPIUser" and password == "test1234!":
        try:
            return BOOKS[book_id]
        except IndexError:
            return "Book not found"
    else:
        return "Invalid User"


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):
    """curl -X 'GET' 'http://127.0.0.1:8000/header' -H 'accept: application/json' -H 'random-header: test'"""
    return {"Random-Header": random_header}


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None):  # query parameter
    """curl -X 'GET' 'http://127.0.0.1:8000/?books_to_return=2' -H 'accept: application/json'"""
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(
            books_to_return=books_to_return
        )  # this raise will trigger the (global) exception handler
    if len(BOOKS) < 1:
        create_books_no_api()
    if books_to_return and len(BOOKS) >= books_to_return > 0:
        return BOOKS[:books_to_return]
    else:
        return BOOKS


@app.post("/", status_code=status.HTTP_201_CREATED)  # create a custom status code
async def create_book(
    book: Book,
):  # not query parameter, this is request body denoted by BaseModel
    """curl -X 'POST' 'http://127.0.0.1:8000/' -H 'accept: application/json' -H 'Content-Type: application/json' \
    -d '{"id": "a96dbb9b-a650-475b-b899-bb4dac1c0466", "title": "Computer Science Pro", "author": "Coding with Eugene",
    "description": "A very nice description of a book", "rating": 75}'
    """
    BOOKS.append(book)
    return book


@app.get("/{book_id}")  # path parameter
async def read_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book  # return Book object? automatically knows how to jsonify it
    raise_item_cannot_be_found_exception()


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    for i, original_book in enumerate(BOOKS):
        if original_book.id == book_id:
            BOOKS[i] = book
            return book
    raise_item_cannot_be_found_exception()


@app.delete("/{book_id}")
async def delete_book(book_id: UUID):
    for i, book in enumerate(BOOKS):
        if book.id == book_id:
            del BOOKS[i]
            return f"ID {book_id} deleted"
    # raise HTTPException(
    #     status_code=404,
    #     detail=f"`book_id` {book_id} not found",
    #     headers={"X-Header-Error": "Nothing to be seen at the UUID"},
    # )
    raise_item_cannot_be_found_exception()


def create_books_no_api():
    book_1 = Book(
        id="a96dbb9b-a650-475b-b899-bb4dac1c0466",
        title="Title 1",
        author="Author 1",
        description="Description 1",
        rating=61,
    )
    book_2 = Book(
        id="a96dbb9b-a650-475b-b899-bb4dac1c0467",
        title="Title 2",
        author="Author 2",
        description="Description 2",
        rating=62,
    )
    book_3 = Book(
        id="a96dbb9b-a650-475b-b899-bb4dac1c0468",
        title="Title 3",
        author="Author 3",
        description="Description 3",
        rating=63,
    )
    book_4 = Book(
        id="a96dbb9b-a650-475b-b899-bb4dac1c0469",
        title="Title 4",
        author="Author 4",
        description="Description 4",
        rating=64,
    )
    BOOKS.extend([book_1, book_2, book_3, book_4])


@app.get(
    "/book/rating/{book_id}", response_model=BookNoRating
)  # change the return type to modify data
async def read_book_no_rating(
    book_id: UUID,
):  # can you not put a BaseModel into a GET request?
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise_item_cannot_be_found_exception()

