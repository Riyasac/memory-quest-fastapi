from fastapi import FastAPI, status, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated
import asyncio
import time
app = FastAPI()

class Item(BaseModel):
    name: str
    price: float


@app.get("/", status_code=status.HTTP_201_CREATED)
def health():
    return {"status": "ok"}


@app.get("/items")
def get_items():
    return ["item1", "item2"]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}


@app.post("/items")
def create_item(item: Item):
    return item


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"updated_id": item_id, "data": item}


@app.patch("/items/{item_id}")
def partial_update(item_id: int, item: dict):
    return {"patched": item_id, "data": item}


@app.delete("/items/{item_id}")
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


def main():
    print("Hello from fastapi-project!")


if __name__ == "__main__":
    main()
