from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List
from app.models import Advertisement, User
from app.schemas import AdvertisementCreate, AdvertisementUpdate, UserCreate, UserUpdate
from app.auth import get_password_hash


# User CRUD
async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    db_user = await get_user(db, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True


async def get_all_users(db: AsyncSession) -> List[User]:
    result = await db.execute(select(User))
    return result.scalars().all()


# Advertisement CRUD
async def create_advertisement(db: AsyncSession, ad_data: AdvertisementCreate, author_id: int) -> Advertisement:
    db_ad = Advertisement(**ad_data.model_dump(), author_id=author_id)
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad


async def get_advertisement(db: AsyncSession, ad_id: int) -> Optional[Advertisement]:
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    return result.scalar_one_or_none()


async def update_advertisement(db: AsyncSession, ad_id: int, ad_data: AdvertisementUpdate) -> Optional[Advertisement]:
    db_ad = await get_advertisement(db, ad_id)
    if not db_ad:
        return None
    update_data = ad_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ad, key, value)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad


async def delete_advertisement(db: AsyncSession, ad_id: int) -> bool:
    db_ad = await get_advertisement(db, ad_id)
    if not db_ad:
        return False
    await db.delete(db_ad)
    await db.commit()
    return True


async def search_advertisements(
        db: AsyncSession,
        title: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
) -> List[Advertisement]:
    query = select(Advertisement)
    if title:
        query = query.where(Advertisement.title.ilike(f"%{title}%"))
    if min_price is not None:
        query = query.where(Advertisement.price >= min_price)
    if max_price is not None:
        query = query.where(Advertisement.price <= max_price)
    result = await db.execute(query)
    return result.scalars().all()


async def get_user_advertisements(db: AsyncSession, user_id: int) -> List[Advertisement]:
    result = await db.execute(select(Advertisement).where(Advertisement.author_id == user_id))
    return result.scalars().all()