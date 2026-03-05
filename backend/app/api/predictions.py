from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class PriceRequest(BaseModel):
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    num_travelers: int = 1
    travel_class: str = "economy"  # economy | business | first


class HotelRequest(BaseModel):
    destination: str
    check_in: date
    check_out: date
    num_guests: int = 1
    hotel_class: int = 3  # stars: 2, 3, 4, 5


class PricePrediction(BaseModel):
    predicted_price: float
    confidence: float
    price_trend: str          # rising | falling | stable
    best_booking_window: str  # "Book now" | "Wait X days"
    price_range: dict         # {"min": X, "max": Y}
    recommendation: str


@router.post("/flight", response_model=PricePrediction)
async def predict_flight_price(
    data: PriceRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict flight prices using ML model."""
    from app.ml.price_predictor.model import FlightPricePredictor

    predictor = FlightPricePredictor()
    result = predictor.predict(
        origin=data.origin,
        destination=data.destination,
        departure_date=data.departure_date,
        return_date=data.return_date,
        num_travelers=data.num_travelers,
        travel_class=data.travel_class,
    )
    return result


@router.post("/hotel", response_model=PricePrediction)
async def predict_hotel_price(
    data: HotelRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict hotel prices using ML model."""
    from app.ml.price_predictor.model import HotelPricePredictor

    predictor = HotelPricePredictor()
    result = predictor.predict(
        destination=data.destination,
        check_in=data.check_in,
        check_out=data.check_out,
        num_guests=data.num_guests,
        hotel_class=data.hotel_class,
    )
    return result
