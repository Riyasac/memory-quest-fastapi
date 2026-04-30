from fastapi import FastAPI, status, Depends, Header, HTTPException, Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated
import asyncio
import time
from enum import Enum
from models import Hero, Team, engine, create_db_and_tables
from sqlmodel import Session, select


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
    # print(f"INSIDE MIDDLEWARE ::: STATUS CODE -> {response.status_code}")
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Team CRUD operations
@app.post("/teams/", response_model=Team, tags=["teams"])
def create_team(team: Team):
    with Session(engine) as session:
        session.add(team)
        session.commit()
        session.refresh(team)
        return team


@app.get("/teams/", response_model=list[Team], tags=["teams"])
def read_teams():
    with Session(engine) as session:
        teams = session.exec(select(Team)).all()
        return teams


@app.get("/teams/{team_id}", response_model=Team, tags=["teams"])
def get_team(team_id: int):
    with Session(engine) as session:
        try:
            team = session.exec(select(Team).where(Team.id == team_id)).one()
            return team
        except Exception as e:
            raise HTTPException(status_code=404, detail="Team not found")


@app.put("/teams/{team_id}", response_model=Team, tags=["teams"])
def update_team(team_id: int, team: Team):
    with Session(engine) as session:
        try:
            team1 = session.exec(select(Team).where(Team.id == team_id)).one()
            team1.name = team.name
            team1.headquarters = team.name
            session.add(team1)
            session.commit()
            session.refresh(team1)
            return team1
        except Exception as e:
            raise HTTPException(status_code=404, detail="Team not found")


@app.delete("/teams/{team_id}", response_model=Team, tags=["teams"])
def delete_team(team_id: int):
    with Session(engine) as session:
        try:
            team1 = session.exec(select(Team).where(Team.id == team_id)).one()
            session.delete(team1)
            session.commit()
            return team1
        except Exception as e:
            raise HTTPException(status_code=404, detail="Team not found")


# Hero CRUD operations
@app.post("/heroes/", response_model=Hero, tags=["heroes"])
def create_hero(hero: Hero):
    with Session(engine) as session:
        
        try:
            team = session.exec(select(Team).where(Team.id == hero.team_id)).one()
        except Exception as e:
            raise HTTPException(status_code=404, detail="Team not found")
        
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/", response_model=list[Hero], tags=["heroes"])
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


@app.get("/heroes/{hero_id}", response_model=Hero, tags=["heroes"])
def get_hero(hero_id: int):
    with Session(engine) as session:
        try:
            hero = session.exec(select(Hero).where(Hero.id == hero_id)).one()
            return hero
        except Exception as e:
            raise HTTPException(status_code=404, detail="Hero not found")


@app.put("/heroes/{hero_id}", response_model=Hero, tags=["heroes"])
def update_hero(hero_id: int, hero: Hero):
    with Session(engine) as session:
        try:
            hero_1 = session.exec(select(Hero).where(Hero.id == hero_id)).one()
            hero_1.name = hero.name
            hero_1.secret_name = hero.secret_name
            hero_1.age = hero.age
            hero_1.team_id = hero.team_id
            session.add(hero_1)
            session.commit()
            session.refresh(hero_1)
            return hero_1
        except Exception as e:
            raise HTTPException(status_code=404, detail="Hero not found")


@app.delete("/heroes/{hero_id}", response_model=Hero, tags=["heroes"])
def delete_hero(hero_id: int):
    with Session(engine) as session:
        try:
            hero_1 = session.exec(select(Hero).where(Hero.id == hero_id)).one()
            session.delete(hero_1)
            session.commit()
            return hero_1
        except Exception as e:
            raise HTTPException(status_code=404, detail="Hero not found")


def main():
    print("Hello from fastapi-project!")


if __name__ == "__main__":
    main()
