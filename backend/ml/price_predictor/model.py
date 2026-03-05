"""
Flight & Hotel Price Predictor using XGBoost.

In production:
- Train on historical Amadeus / Skyscanner data
- Features: lead_time, season, route, day_of_week, demand signals
- Retrain weekly with fresh price data

Currently: rule-based simulation for MVP (replace with trained model pkl)
"""
import numpy as np
from datetime import date, timedelta
from typing import Optional


class FlightPricePredictor:
    """XGBoost-based flight price predictor."""

    # Seasonal multipliers (month index 1-12)
    SEASON_MULTIPLIERS = {
        1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95,
        5: 1.00, 6: 1.20, 7: 1.35, 8: 1.30,
        9: 1.00, 10: 0.95, 11: 0.85, 12: 1.25,
    }

    BASE_PRICES = {
        "economy": 350,
        "business": 1200,
        "first": 3000,
    }

    def predict(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date],
        num_travelers: int,
        travel_class: str,
    ) -> dict:
        today = date.today()
        lead_time = (departure_date - today).days

        # Feature engineering
        season_mult = self.SEASON_MULTIPLIERS.get(departure_date.month, 1.0)
        day_of_week_mult = 1.15 if departure_date.weekday() in [4, 6] else 1.0  # Fri/Sun premium
        lead_time_mult = self._lead_time_multiplier(lead_time)

        base = self.BASE_PRICES.get(travel_class, 350)
        predicted = base * season_mult * day_of_week_mult * lead_time_mult
        predicted_per_person = round(predicted, 2)
        total_price = round(predicted_per_person * num_travelers, 2)

        # Simulate confidence based on lead time
        confidence = min(0.95, 0.6 + (lead_time / 365) * 0.35)

        # Trend: if lead time < 14 days, prices are rising
        if lead_time < 14:
            trend = "rising"
            recommendation = "Book now — prices are increasing as your travel date approaches."
            booking_window = "Book immediately"
        elif lead_time > 60:
            trend = "stable"
            recommendation = "Prices are stable. You can wait a few more weeks but don't delay past 6 weeks out."
            booking_window = "Book within 3-4 weeks"
        else:
            trend = "falling" if lead_time_mult > 1.1 else "stable"
            recommendation = "Good time to book — you're in the optimal booking window."
            booking_window = "Book now for best price"

        return {
            "predicted_price": total_price,
            "confidence": round(confidence, 2),
            "price_trend": trend,
            "best_booking_window": booking_window,
            "price_range": {
                "min": round(total_price * 0.85, 2),
                "max": round(total_price * 1.20, 2),
            },
            "recommendation": recommendation,
        }

    def _lead_time_multiplier(self, days: int) -> float:
        """Price multiplier based on how far in advance booking is made."""
        if days < 7:
            return 1.45    # Last-minute premium
        elif days < 14:
            return 1.30
        elif days < 30:
            return 1.10
        elif days < 60:
            return 1.00    # Optimal booking window
        elif days < 120:
            return 0.95
        else:
            return 1.05    # Too far out — prices haven't dropped yet


class HotelPricePredictor:
    """XGBoost-based hotel price predictor."""

    BASE_PRICES_PER_NIGHT = {
        2: 60,
        3: 110,
        4: 200,
        5: 400,
    }

    SEASON_MULTIPLIERS = {
        1: 0.80, 2: 0.75, 3: 0.90, 4: 0.95,
        5: 1.00, 6: 1.25, 7: 1.40, 8: 1.35,
        9: 1.05, 10: 0.95, 11: 0.85, 12: 1.30,
    }

    def predict(
        self,
        destination: str,
        check_in: date,
        check_out: date,
        num_guests: int,
        hotel_class: int,
    ) -> dict:
        num_nights = (check_out - check_in).days
        season_mult = self.SEASON_MULTIPLIERS.get(check_in.month, 1.0)
        base_per_night = self.BASE_PRICES_PER_NIGHT.get(hotel_class, 110)
        lead_time = (check_in - date.today()).days

        price_per_night = base_per_night * season_mult
        total_price = round(price_per_night * num_nights, 2)

        trend = "rising" if lead_time < 21 else "stable"
        booking_window = "Book now" if lead_time < 30 else "Book 3-4 weeks before check-in"

        return {
            "predicted_price": total_price,
            "confidence": 0.82,
            "price_trend": trend,
            "best_booking_window": booking_window,
            "price_range": {
                "min": round(total_price * 0.80, 2),
                "max": round(total_price * 1.25, 2),
            },
            "recommendation": (
                f"Expected {num_nights} nights at a {hotel_class}-star hotel. "
                f"{'Book soon — availability is dropping.' if lead_time < 30 else 'Prices are currently stable.'}"
            ),
        }
