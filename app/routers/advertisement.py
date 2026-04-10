from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, require_admin
from app.models import User, UserRole

router = APIRouter(prefix="/advertisement", tags=["advertisements"])


@router.post("/", response_model=schemas.AdvertisementResponse, status_code=201)
async def create_ad(
        ad_data: schemas.AdvertisementCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    return await crud.create_advertisement(db, ad_data, current_user.id)


@router.patch("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
async def update_ad(
        advertisement_id: int,
        ad_data: schemas.AdvertisementUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.role != UserRole.ADMIN and ad.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own advertisements"
        )

    updated = await crud.update_advertisement(db, advertisement_id, ad_data)
    return updated


@router.delete("/{advertisement_id}", status_code=204)
async def delete_ad(
        advertisement_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    if current_user.role != UserRole.ADMIN and ad.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own advertisements"
        )

    await crud.delete_advertisement(db, advertisement_id)
    return


@router.get("/{advertisement_id}", response_model=schemas.AdvertisementResponse)
async def get_ad(
        advertisement_id: int,
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: AsyncSession = Depends(get_db)
):
    ad = await crud.get_advertisement(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@router.get("/", response_model=List[schemas.AdvertisementResponse])
async def search_ads(
        title: Optional[str] = Query(None, description="Search by title (partial match)"),
        min_price: Optional[float] = Query(None, description="Minimum price"),
        max_price: Optional[float] = Query(None, description="Maximum price"),
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: AsyncSession = Depends(get_db)
):
    return await crud.search_advertisements(db, title, min_price, max_price)