import os
from sqlmodel import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@db/maindb"
)

engine = create_engine(DATABASE_URL)
