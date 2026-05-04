from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from utils.security import decode_access_token, oauth2_scheme
from dependencies.session import get_session
from sqlmodel import select

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    print("Received token:", token)  # Debug statement
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    username = payload["sub"]
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
