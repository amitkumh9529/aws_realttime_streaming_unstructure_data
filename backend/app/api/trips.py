from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.trip import Trip, TripStatus, Budget

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────

class TripCreate(BaseModel):
    title: str
    destination: str
    origin: Optional[str] = None
    start_date: date
    end_date: date
    num_travelers: int = 1
    travel_style: Optional[str] = "comfort"
    interests: List[str] = []
    total_budget: Optional[float] = None
    currency: str = "USD"


class TripResponse(BaseModel):
    id: int
    title: str
    destination: str
    origin: Optional[str]
    start_date: date
    end_date: date
    num_travelers: int
    travel_style: Optional[str]
    interests: List[str]
    status: TripStatus

    class Config:
        from_attributes = True


# ─── Routes ───────────────────────────────────────────────────────────

@router.get("/", response_model=List[TripResponse])
async def list_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all trips for the current user."""
    result = await db.execute(
        select(Trip).where(Trip.user_id == current_user.id).order_by(Trip.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    data: TripCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new trip."""
    if data.start_date >= data.end_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    trip = Trip(
        user_id=current_user.id,
        title=data.title,
        destination=data.destination,
        origin=data.origin,
        start_date=data.start_date,
        end_date=data.end_date,
        num_travelers=data.num_travelers,
        travel_style=data.travel_style,
        interests=data.interests,
    )
    db.add(trip)
    await db.flush()  # Get the trip ID

    # Create default budget if provided
    if data.total_budget:
        budget = Budget(
            trip_id=trip.id,
            total_budget=data.total_budget,
            currency=data.currency,
        )
        db.add(budget)

    await db.commit()
    await db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    allowed = {"title", "destination", "start_date", "end_date", "num_travelers", "travel_style", "interests", "status"}
    for key, value in data.items():
        if key in allowed:
            setattr(trip, key, value)

    await db.commit()
    await db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a trip."""
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    await db.delete(trip)
    await db.commit()
