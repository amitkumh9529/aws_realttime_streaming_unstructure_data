from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx

from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class WeatherRequest(BaseModel):
    destination: str
    travel_month: int   # 1-12
    interests: List[str] = []


class WeatherRecommendation(BaseModel):
    destination: str
    travel_month: int
    suitability_score: float      # 0-100
    temperature_range: dict       # {"min": X, "max": Y, "unit": "C"}
    conditions: str               # "Sunny and warm", etc.
    recommendation: str           # "Great time to visit" | "Consider another month"
    best_months: List[int]        # Best months to visit
    packing_suggestions: List[str]
    activity_suitability: dict    # {"beach": 90, "hiking": 70, ...}


@router.post("/recommend", response_model=WeatherRecommendation)
async def weather_recommendation(
    data: WeatherRequest,
    current_user: User = Depends(get_current_user),
):
    """Get weather-based travel recommendation for a destination and month."""
    from app.ml.weather.recommender import WeatherRecommender

    recommender = WeatherRecommender(api_key=settings.OPENWEATHER_API_KEY)
    result = await recommender.recommend(
        destination=data.destination,
        travel_month=data.travel_month,
        interests=data.interests,
    )
    return result


@router.get("/current/{destination}")
async def current_weather(
    destination: str,
    current_user: User = Depends(get_current_user),
):
    """Get current weather for a destination."""
    if not settings.OPENWEATHER_API_KEY:
        return {"message": "Weather API key not configured", "destination": destination}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": destination,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Could not find weather for {destination}")

        data = response.json()
        return {
            "destination": destination,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
        }
