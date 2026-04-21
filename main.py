from fastapi import FastAPI, status, Depends, Header, HTTPException, Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated
import asyncio
import time
from enum import Enum


app = FastAPI()


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    price: float
    description: str | None = Field(default=None, examples=["A very nice Item"])
    tax: float | None = None
    is_active: bool = True
    tags: list = []
    image: Image | None = None

class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


@app.get("/", status_code=status.HTTP_201_CREATED)
def health():
    return {"status": "ok"}


@app.get("/items", tags=["items"])
def get_items():
    return ["item1", "item2"]


@app.get("/items/{item_id}", tags=["items"])
def get_item(item_id: int):
    return {"item_id": item_id}


@app.post(
    "/items",
    tags=["items"],
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
def create_item(item: Item):
    return item


@app.put("/items/{item_id}", tags=["items"])
def update_item(item_id: int, item: Item):
    return {"updated_id": item_id, "data": item}


@app.patch("/items/{item_id}", tags=["items"])
def partial_update(item_id: int, item: dict):
    return {"patched": item_id, "data": item}


@app.delete("/items/{item_id}", tags=["items"])
def delete_item(item_id: int):
    return {"deleted": item_id}


@app.get("/search")
def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}


def common_params():
    return {"limit": 10}


@app.get("/products")
def get_products(params: dict = Depends(common_params)):
    return params


@app.get('/header')
def get_header(token: Annotated[str, Header()]):
    return {"token": token}


@app.get('/error')
def error():
    return HTTPException(status_code=404, detail="Not Found")


@app.get("/sync")
def sync_route():
    time.sleep(2)
    return {"message":"sync"}


@app.get("/async")
async def async_route():
    await asyncio.sleep(2)
    return {"message":"async"}


@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    print(f"INSIDE MIDDLEWARE ::: STATUS CODE -> {response.status_code}")
    return response


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/orders/{order_status}")
async def get_model(order_status: OrderStatus):
    if order_status is OrderStatus.pending:
        return {"order_status": order_status, "message": "Pending orders"}

    if order_status.value == "completed":
        return {"order_status": order_status, "message": "Completed orders"}

    return {"order_status": order_status, "message": "Cancelled orders"}


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


def main():
    print("Hello from fastapi-project!")


if __name__ == "__main__":
    main()
