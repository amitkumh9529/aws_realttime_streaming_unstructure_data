from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.trip import Trip, Itinerary

router = APIRouter()


class ItineraryRequest(BaseModel):
    trip_id: int
    additional_preferences: Optional[str] = None


class ItineraryResponse(BaseModel):
    id: int
    trip_id: int
    days: List[dict]
    generated_by: str

    class Config:
        from_attributes = True


@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(
    data: ItineraryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-powered itinerary for a trip."""
    # Get trip
    result = await db.execute(
        select(Trip).where(Trip.id == data.trip_id, Trip.user_id == current_user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    num_days = (trip.end_date - trip.start_date).days + 1

    # Build prompt
    prompt = f"""You are an expert travel planner. Create a detailed {num_days}-day itinerary for:

Destination: {trip.destination}
Travel dates: {trip.start_date} to {trip.end_date}
Number of travelers: {trip.num_travelers}
Travel style: {trip.travel_style or 'comfort'}
Interests: {', '.join(trip.interests) if trip.interests else 'general sightseeing'}
{f'Additional preferences: {data.additional_preferences}' if data.additional_preferences else ''}

Return ONLY a JSON array (no markdown, no explanation) with this structure:
[
  {{
    "day": 1,
    "date": "YYYY-MM-DD",
    "theme": "Day theme title",
    "activities": [
      {{
        "time": "09:00",
        "title": "Activity name",
        "description": "Brief description",
        "location": "Place name",
        "duration_minutes": 120,
        "type": "sightseeing|food|transport|leisure|culture",
        "cost_estimate": 25
      }}
    ],
    "accommodation_tip": "Where to stay tonight",
    "daily_budget_estimate": 150
  }}
]"""

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)
        days = parsed if isinstance(parsed, list) else parsed.get("itinerary", [])

    except Exception as e:
        # Fallback: return a sample structure if OpenAI not configured
        days = _generate_sample_itinerary(trip.destination, num_days, trip.start_date)

    # Save or update itinerary
    existing = await db.execute(select(Itinerary).where(Itinerary.trip_id == trip.id))
    itinerary = existing.scalar_one_or_none()

    if itinerary:
        itinerary.days = days
    else:
        itinerary = Itinerary(
            trip_id=trip.id,
            days=days,
            generated_by="ai",
            generation_prompt=prompt[:2000],
        )
        db.add(itinerary)

    await db.commit()
    await db.refresh(itinerary)
    return itinerary


@router.get("/{trip_id}", response_model=ItineraryResponse)
async def get_itinerary(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get itinerary for a trip."""
    result = await db.execute(
        select(Itinerary)
        .join(Trip)
        .where(Itinerary.trip_id == trip_id, Trip.user_id == current_user.id)
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(status_code=404, detail="No itinerary found for this trip")
    return itinerary


def _generate_sample_itinerary(destination: str, num_days: int, start_date) -> list:
    """Fallback sample itinerary when OpenAI is not configured."""
    from datetime import timedelta
    days = []
    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        days.append({
            "day": i + 1,
            "date": str(current_date),
            "theme": f"Exploring {destination} - Day {i + 1}",
            "activities": [
                {
                    "time": "09:00",
                    "title": "Morning exploration",
                    "description": f"Discover the highlights of {destination}",
                    "location": destination,
                    "duration_minutes": 180,
                    "type": "sightseeing",
                    "cost_estimate": 20,
                },
                {
                    "time": "13:00",
                    "title": "Local lunch",
                    "description": "Try authentic local cuisine",
                    "location": f"Local restaurant in {destination}",
                    "duration_minutes": 90,
                    "type": "food",
                    "cost_estimate": 30,
                },
                {
                    "time": "15:00",
                    "title": "Afternoon sightseeing",
                    "description": "Visit popular attractions",
                    "location": destination,
                    "duration_minutes": 180,
                    "type": "culture",
                    "cost_estimate": 15,
                },
            ],
            "accommodation_tip": f"Stay centrally in {destination} for easy access",
            "daily_budget_estimate": 150,
        })
    return days
