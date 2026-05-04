from fastapi import FastAPI, status, Depends, HTTPException
from sqlmodel import SQLModel
from services.db import engine
from routers import user_router, hero_router, team_router
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import authenticate_user, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.session import get_session
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(root_path="/api/v1")


origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_201_CREATED)
async def health():
    return {"status": "ok"}


# Create tables at startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Include routers
app.include_router(user_router.router)
app.include_router(hero_router.router)
app.include_router(team_router.router)


def main():
    print("Hello from fastapi-project!")


if __name__ == "__main__":
    main()
