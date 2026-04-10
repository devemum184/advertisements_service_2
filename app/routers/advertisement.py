from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/advertisement", tags=["advertisements"])

@router.post("/", response_model=schemas.AdvertisementResponse, status_code=201)
async def create_ad(ad_data: schemas.AdvertisementCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_advertisement(db, ad_data)

@router.patch("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
async def update_ad(advertisement_id: int, ad_data: schemas.AdvertisementUpdate, db: AsyncSession = Depends(get_db)):
    ad = await crud.update_advertisement(db, advertisement_id, ad_data)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@router.delete("/{advertisement_id}", status_code=204)
async def delete_ad(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_advertisement(db, advertisement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return

@router.get("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
async def get_ad(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@router.get("/", response_model=List[schemas.AdvertisementResponse])
async def search_ads(
    title: Optional[str] = Query(None, description="Search by title (partial match)"),
    author: Optional[str] = Query(None, description="Search by author (partial match)"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    db: AsyncSession = Depends(get_db)
):
    return await crud.search_advertisements(db, title, author, min_price, max_price)