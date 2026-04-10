from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_owner_or_admin, require_admin
from app.models import User

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=201)
async def create_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return await crud.create_user(db, user_data)

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[schemas.UserResponse])
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_all_users(db)

@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    current_user: User = Depends(lambda: require_owner_or_admin(user_id)),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Depends(lambda: require_owner_or_admin(user_id)),
    db: AsyncSession = Depends(get_db)
):
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return