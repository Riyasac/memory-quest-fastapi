from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from dependencies.session import get_session
from schemas.user_schema import UserCreate
from utils.security import hash_password
from utils.pagination import paginate_query
from dependencies.user import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# User CRUD operations with uniqueness checks for username, email, and phone number
@router.post("/", response_model=UserCreate)
async def create_user(
    user_create: UserCreate, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if username already exists
    statement = select(User).where(User.username == user_create.username)
    existing_user = await session.execute(statement)

    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check if email already exists
    statement = select(User).where(User.email == user_create.email)
    existing_email = await session.execute(statement)
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # Check if email already exists
    if user_create.phone_number:
        print("Checking phone number:", user_create.phone_number)  # Debug statement
        statement = select(User).where(User.phone_number == user_create.phone_number)
        existing_phone_number = await session.execute(statement)
        if existing_phone_number.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Phonenumber already exists"
            )

    # Hash the password before saving
    hashed_pass = hash_password(user_create.password)
    user_create.password = hashed_pass
    # Convert pydantic model to SQLModel instance
    user = User(**user_create.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/", response_model=dict)
async def read_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = Query(default=10, le=100),
):
    data = await paginate_query(
        session=session,
        model=User,
        offset=offset,
        limit=limit,
        order_by=User.id.desc(),
        base_url="/users/",
    )
    return data


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()  # returns User or None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserCreate)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

        # --- Uniqueness checks ---
    if user_update.username and user_update.username != db_user.username:
        existing_user = await session.execute(
            select(User).where(User.username == user_update.username)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")

    if user_update.email and user_update.email != db_user.email:
        existing_email = await session.execute(
            select(User).where(User.email == user_update.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

    if user_update.phone_number and user_update.phone_number != db_user.phone_number:
        existing_phone = await session.execute(
            select(User).where(User.phone_number == user_update.phone_number)
        )
        if existing_phone.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone number already exists")

    # --- Apply updates ---
    user_data = user_update.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in user_data and user_data["password"]:
        user_data["password"] = hash_password(user_data["password"])

    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await session.delete(user)
    await session.commit()
    return user
