from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items")
def get_items():
    return ["item1", "item2"]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}


@app.post("/items")
def create_item(item: Item):
    return {"created": item}


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


def main():
    print("Hello from fastapi-project!")


if __name__ == "__main__":
    main()
