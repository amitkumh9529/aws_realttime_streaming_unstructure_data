from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TripStatus(str, enum.Enum):
    PLANNING = "planning"
    BOOKED = "booked"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    destination_lat = Column(Float, nullable=True)
    destination_lng = Column(Float, nullable=True)
    origin = Column(String(255), nullable=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    num_travelers = Column(Integer, default=1)
    travel_style = Column(String(100), nullable=True)  # budget | comfort | luxury
    interests = Column(JSON, default=[])               # ["beach", "culture", "food"]

    status = Column(Enum(TripStatus), default=TripStatus.PLANNING)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="trips")
    itinerary = relationship("Itinerary", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    budget = relationship("Budget", back_populates="trip", uselist=False, cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)

    days = Column(JSON, default=[])       # [{day: 1, activities: [...]}]
    generated_by = Column(String(50), default="ai")  # ai | manual
    generation_prompt = Column(String(2000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trip = relationship("Trip", back_populates="itinerary")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)

    total_budget = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")

    # AI-optimized breakdown
    flights_budget = Column(Float, default=0)
    hotel_budget = Column(Float, default=0)
    food_budget = Column(Float, default=0)
    activities_budget = Column(Float, default=0)
    transport_budget = Column(Float, default=0)
    misc_budget = Column(Float, default=0)

    # Actual spent (updated as user logs expenses)
    actual_spent = Column(JSON, default={})

    # ML predicted costs
    predicted_flight_cost = Column(Float, nullable=True)
    predicted_hotel_cost = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trip = relationship("Trip", back_populates="budget")
