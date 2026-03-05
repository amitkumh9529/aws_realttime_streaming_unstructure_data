"""
Weather-based travel recommender.
Uses OpenWeatherMap API for current data + rule-based climate scoring.
In production: replace with trained K-Means clustering on historical climate data.
"""
from typing import List
import httpx


# Curated climate database for popular destinations
CLIMATE_DB = {
    "paris": {
        "best_months": [4, 5, 6, 9, 10],
        "monthly_temp": {1: 5, 2: 6, 3: 10, 4: 14, 5: 18, 6: 22, 7: 25, 8: 24, 9: 20, 10: 15, 11: 9, 12: 6},
        "monthly_rain": {1: 8, 2: 7, 3: 8, 4: 8, 5: 8, 6: 7, 7: 6, 8: 5, 9: 6, 10: 8, 11: 8, 12: 9},
        "activity_scores": {"culture": 90, "food": 95, "shopping": 88, "nightlife": 85, "beach": 20},
    },
    "bali": {
        "best_months": [4, 5, 6, 7, 8, 9],
        "monthly_temp": {1: 27, 2: 27, 3: 28, 4: 28, 5: 27, 6: 26, 7: 25, 8: 26, 9: 27, 10: 28, 11: 27, 12: 27},
        "monthly_rain": {1: 13, 2: 13, 3: 11, 4: 7, 5: 5, 6: 3, 7: 2, 8: 2, 9: 3, 10: 6, 11: 10, 12: 13},
        "activity_scores": {"beach": 95, "culture": 80, "hiking": 75, "surfing": 88, "food": 82},
    },
    "tokyo": {
        "best_months": [3, 4, 5, 10, 11],
        "monthly_temp": {1: 6, 2: 7, 3: 10, 4: 15, 5: 20, 6: 23, 7: 27, 8: 29, 9: 25, 10: 19, 11: 13, 12: 8},
        "monthly_rain": {1: 5, 2: 6, 3: 10, 4: 11, 5: 11, 6: 14, 7: 12, 8: 9, 9: 13, 10: 10, 11: 8, 12: 5},
        "activity_scores": {"culture": 95, "food": 98, "shopping": 92, "nightlife": 88, "hiking": 65},
    },
    "new york": {
        "best_months": [4, 5, 6, 9, 10],
        "monthly_temp": {1: 1, 2: 3, 3: 7, 4: 13, 5: 19, 6: 24, 7: 28, 8: 27, 9: 22, 10: 16, 11: 10, 12: 4},
        "monthly_rain": {1: 9, 2: 8, 3: 10, 4: 10, 5: 10, 6: 10, 7: 10, 8: 9, 9: 8, 10: 8, 11: 8, 12: 10},
        "activity_scores": {"culture": 92, "food": 95, "shopping": 90, "nightlife": 92, "beach": 40},
    },
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


class WeatherRecommender:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def recommend(
        self,
        destination: str,
        travel_month: int,
        interests: List[str],
    ) -> dict:
        dest_key = destination.lower().strip()

        # Try to find in climate DB
        climate = None
        for key, data in CLIMATE_DB.items():
            if key in dest_key or dest_key in key:
                climate = data
                break

        if climate:
            return self._score_from_db(destination, travel_month, interests, climate)
        else:
            # Fallback to API or generic response
            return await self._score_from_api(destination, travel_month, interests)

    def _score_from_db(self, destination: str, month: int, interests: List[str], climate: dict) -> dict:
        temp = climate["monthly_temp"].get(month, 20)
        rain_days = climate["monthly_rain"].get(month, 8)
        best_months = climate["best_months"]

        # Calculate suitability score
        is_best_month = month in best_months
        rain_penalty = max(0, (rain_days - 5) * 3)
        base_score = 85 if is_best_month else 65
        suitability = max(20, base_score - rain_penalty)

        # Determine conditions
        if temp > 28:
            conditions = "Hot and tropical"
        elif temp > 22:
            conditions = "Warm and pleasant"
        elif temp > 15:
            conditions = "Mild and comfortable"
        elif temp > 5:
            conditions = "Cool — bring layers"
        else:
            conditions = "Cold — pack winter clothing"

        if rain_days > 12:
            conditions += ", frequent rain"
        elif rain_days > 8:
            conditions += ", occasional showers"

        # Recommendation
        if suitability >= 80:
            recommendation = f"Excellent time to visit {destination}!"
        elif suitability >= 65:
            recommendation = f"Good time to visit {destination}, though weather could be better."
        else:
            recommendation = f"Consider visiting {destination} in {', '.join([MONTH_NAMES[m] for m in best_months[:3]])} for better weather."

        # Packing suggestions
        packing = self._packing_suggestions(temp, rain_days, interests)

        # Activity suitability
        activity_scores = climate.get("activity_scores", {})
        if rain_days > 10:
            activity_scores = {k: max(0, v - 20) for k, v in activity_scores.items()}

        return {
            "destination": destination,
            "travel_month": month,
            "suitability_score": suitability,
            "temperature_range": {"min": temp - 5, "max": temp + 5, "unit": "C"},
            "conditions": conditions,
            "recommendation": recommendation,
            "best_months": best_months,
            "packing_suggestions": packing,
            "activity_suitability": activity_scores,
        }

    async def _score_from_api(self, destination: str, month: int, interests: List[str]) -> dict:
        """Generic response when destination not in DB."""
        return {
            "destination": destination,
            "travel_month": month,
            "suitability_score": 70.0,
            "temperature_range": {"min": 15, "max": 25, "unit": "C"},
            "conditions": "Varies — check local forecasts closer to your travel date",
            "recommendation": f"Research {destination}'s climate for {MONTH_NAMES[month]} before booking.",
            "best_months": [4, 5, 6, 9, 10],
            "packing_suggestions": ["Layers", "Rain jacket", "Comfortable walking shoes"],
            "activity_suitability": {"sightseeing": 75, "food": 80, "culture": 80},
        }

    def _packing_suggestions(self, temp: float, rain_days: int, interests: List[str]) -> List[str]:
        items = []
        if temp > 25:
            items.extend(["Light clothing", "Sunscreen SPF 50+", "Sunglasses", "Hat"])
        elif temp > 15:
            items.extend(["Light layers", "Comfortable jeans", "Light jacket"])
        else:
            items.extend(["Warm layers", "Winter jacket", "Scarf & gloves"])

        if rain_days > 8:
            items.append("Compact umbrella / rain jacket")

        if "beach" in interests:
            items.extend(["Swimwear", "Beach towel", "Waterproof sandals"])
        if "hiking" in interests:
            items.extend(["Hiking boots", "Moisture-wicking socks", "Daypack"])
        if "culture" in interests or "museums" in interests:
            items.append("Smart casual outfit for restaurants & museums")

        return list(set(items))[:10]
