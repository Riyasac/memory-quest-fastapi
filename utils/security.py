from datetime import datetime, timedelta
from jose import JWTError, jwt
from argon2 import PasswordHasher
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Argon2 password hasher instance
pwd_context = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -------------------------
# Password Hashing
# -------------------------
def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against an Argon2 hash."""
    try:
        return pwd_context.verify(hashed, password)
    except Exception:
        return False


# -------------------------
# JWT Token Helpers
# -------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with an expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token."""
    print("started here")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# -------------------------
# User Authentication
# -------------------------
async def get_current_user(session: AsyncSession, username: str) -> User | None:
    """Fetch a user from the database by username."""
    result = await session.execute(select(User).where(User.username == username, User.is_active == True))
    return result.scalar_one_or_none()


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | None:
    """Authenticate a user by verifying password against stored hash."""
    user = await get_current_user(session, username)
    if not user:
        return None
    if not verify_password(password, user.password):  # password is hashed in DB
        return None
    return user
