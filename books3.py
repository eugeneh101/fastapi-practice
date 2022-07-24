from typing import Dict
from typing import Optional

from fastapi import FastAPI, Query, Body
from pydantic import BaseModel

app = FastAPI()


@app.get("/docs")
def silliest(
    # silly: str,
    sillier: str,
):
    # print(silly)
    # return silly
    return sillier


# @app.get("/")
# def test(
#     # silly: str,
#     sillier: Dict[str, float],
# ):
#     # print(silly)
#     # return silly
#     return sillier


@app.get("/")
# def process_items(prices: Dict[str, float]):
def process_items(prices: Dict):
    for item_name, item_price in prices.items():
        print(item_name)
        print(item_price)
    return prices


@app.get("/silly/")
def another_silly(bob: str = Query(max_length=30)):
    print(bob)
    return str(type(bob))


class Item(BaseModel):
    name: str
    price: float


class User(BaseModel):
    username: str
    password: str


class ItemUser(BaseModel):
    item: Item
    user: User


@app.put("/attempt1/")
async def update_item(item: Item, user: User):
    return {"item": item, "user": user}


@app.put("/attempt2/")
async def update_item(item_user: ItemUser):
    return {"item_user": item_user}


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item = Body(  # seems that FastAPI can only show example if there exists 1 BaseModel
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {"name": "Bar", "price": "35.4",},
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {"name": "Baz", "price": "thirty five point four",},
            },
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results
