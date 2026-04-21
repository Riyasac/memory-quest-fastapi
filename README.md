# FastAPI Basics

## 1. Introduction
FastAPI is a modern Python web framework for building APIs with high performance using type hints.

---

## 2. Key Features
- Automatic Swagger UI (`/docs`)
- ReDoc (`/redoc`)
- Async support (high concurrency)
- Pydantic validation
- Dependency Injection system
- Lightweight and fast

---

## 3. Installation (Using uv)
```bash
pip install uv
uv --version
uv init fastapi-project
cd fastapi-project
uv add fastapi uvicorn
```

---

## 4. Basic App
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
```

Run:
```bash
uv run uvicorn main:app --reload
```

---

## 5. HTTP Methods (CRUD Examples)

### GET (Read)
```python
@app.get("/items")
def get_items():
    return ["item1", "item2"]

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

### POST (Create)
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"created": item}
```

### PUT (Update full)
```python
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"updated_id": item_id, "data": item}
```

### PATCH (Partial update)
```python
@app.patch("/items/{item_id}")
def partial_update(item_id: int, item: dict):
    return {"patched": item_id, "data": item}
```

### DELETE
```python
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"deleted": item_id}
```

---

## 6. Query Parameters
```python
@app.get("/search")
def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}
```

---

## 7. Path vs Query
- **Path** → required (`/items/1`)
- **Query** → optional (`/items?limit=10`)

---

## 8. Request Body Validation
```python
class User(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: User):
    return user
```

---

## 9. Response Model
```python
@app.get("/user", response_model=User)
def get_user():
    return {"name": "John", "age": 25}
```

---

## 10. Dependency Injection (Depends)
```python
from fastapi import Depends

def common_params():
    return {"limit": 10}

@app.get("/products")
def get_products(params: dict = Depends(common_params)):
    return params
```

---

## 11. Headers & Annotated
```python
from typing import Annotated
from fastapi import Header

@app.get("/header")
def get_header(token: Annotated[str, Header()]):
    return {"token": token}
```

---

## 12. Status Codes
```python
from fastapi import status

@app.post("/create", status_code=status.HTTP_201_CREATED)
def create():
    return {"message": "created"}
```

---

## 13. Error Handling
```python
from fastapi import HTTPException

@app.get("/error")
def error():
    raise HTTPException(status_code=404, detail="Not Found")
```

---

## 14. Async vs Sync
```python
import asyncio

@app.get("/async")
async def async_route():
    await asyncio.sleep(1)
    return {"msg": "async"}
```

```python
import time

@app.get("/sync")
def sync_route():
    time.sleep(1)
    return {"msg": "sync"}
```

---

## 15. Middleware Example
```python
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    return response
```

---

## 16. Project Structure
```
fastapi-project/
├── main.py
├── routers/
├── models/
├── schemas/
├── services/
└── dependencies/
```

---

## 17. Common Mistakes
- Using blocking code in async
- Not validating input
- Poor project structure
- Ignoring `response_model`

---

## 18. Next Steps
- Database integration
- JWT Authentication
- Background tasks
- Docker deployment
