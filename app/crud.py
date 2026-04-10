from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate

async def create_advertisement(db: AsyncSession, ad_data: AdvertisementCreate) -> Advertisement:
    db_ad = Advertisement(**ad_data.model_dump())
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
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Advertisement]:
    query = select(Advertisement)
    if title:
        query = query.where(Advertisement.title.ilike(f"%{title}%"))
    if author:
        query = query.where(Advertisement.author.ilike(f"%{author}%"))
    if min_price is not None:
        query = query.where(Advertisement.price >= min_price)
    if max_price is not None:
        query = query.where(Advertisement.price <= max_price)
    result = await db.execute(query)
    return result.scalars().all()