from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None


class TravelPlanRequest(BaseModel):
    center_location: LocationRequest
    start_date: datetime
    end_date: datetime
    preferences: Optional[List[str]] = None
    travel_mode: Optional[str] = "walking"  # walking, driving, transit


class PointOfInterest(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    description: str
    recommended_duration: Optional[str] = None


class DailyPlan(BaseModel):
    date: datetime
    poi_list: List[PointOfInterest]
    description: str


class TravelPlanResponse(BaseModel):
    plan_id: str = Field(..., description="生成的旅游计划ID")
    center_location: LocationRequest
    start_date: datetime
    end_date: datetime
    daily_plans: List[DailyPlan]
    overview: str = Field(..., description="旅游计划概览")