from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.profile import Profile as ProfileModel
from app.schemas.profile import Profile, ProfileCreate, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _get_profile_or_404(db: Session, profile_id: int) -> ProfileModel:
    profile = db.get(ProfileModel, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.post("", response_model=Profile, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_create: ProfileCreate,
    db: Session = Depends(get_db),
) -> ProfileModel:
    profile = ProfileModel(**profile_create.model_dump(mode="json"))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=list[Profile])
def list_profiles(db: Session = Depends(get_db)) -> list[ProfileModel]:
    return list(db.scalars(select(ProfileModel).order_by(ProfileModel.id)))


@router.get("/{profile_id}", response_model=Profile)
def get_profile(profile_id: int, db: Session = Depends(get_db)) -> ProfileModel:
    return _get_profile_or_404(db, profile_id)


@router.patch("/{profile_id}", response_model=Profile)
def update_profile(
    profile_id: int,
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
) -> ProfileModel:
    existing_profile = _get_profile_or_404(db, profile_id)
    update_data = profile_update.model_dump(exclude_unset=True, mode="json")

    for field, value in update_data.items():
        setattr(existing_profile, field, value)

    db.commit()
    db.refresh(existing_profile)
    return existing_profile
