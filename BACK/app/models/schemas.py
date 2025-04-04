from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, timedelta


class ScenicSpot(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: str


class TravelData(BaseModel):
    scenicSpots: List[ScenicSpot]
    travelMode: str
    travelDays: str  # 注意这里是字符串类型，需要转换为整数


class TravelPlanRequest(BaseModel):
    city: str
    centerName: str
    travelData: TravelData


class PointOfInterest(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    description: str
    recommended_duration: Optional[str] = None


class DailyPlan(BaseModel):
    day: int  # 第几天
    date: Optional[date] = None  # 可选日期
    poi_list: List[PointOfInterest]
    description: str


class TravelPlanResponse(BaseModel):
    plan_id: str = Field(..., description="生成的旅游计划ID")
    city: str
    center_name: str
    travel_days: int
    travel_mode: str
    daily_plans: List[DailyPlan]
    overview: str = Field(..., description="旅游计划概览")