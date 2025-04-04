from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import TravelPlanRequest, TravelPlanResponse
from app.services.travel_service import TravelService
from app.core.security import verify_wx_request
import uuid

router = APIRouter()


@router.post("/generate-plan", response_model=TravelPlanResponse)
async def generate_travel_plan(
        request: TravelPlanRequest,
        travel_service: TravelService = Depends(),
        authenticated: bool = Depends(verify_wx_request)
):
    """根据中心位置和计划天数生成旅游计划"""
    try:
        # 将字符串类型的旅行天数转换为整数
        travel_days = int(request.travelData.travelDays)

        # 调用旅游服务生成计划
        travel_plan = await travel_service.generate_plan(
            city=request.city,
            center_name=request.centerName,
            scenic_spots=request.travelData.scenicSpots,
            travel_days=travel_days,
            travel_mode=request.travelData.travelMode
        )

        # 生成计划ID
        plan_id = str(uuid.uuid4())

        # 构建响应
        response = TravelPlanResponse(
            plan_id=plan_id,
            city=request.city,
            center_name=request.centerName,
            travel_days=travel_days,
            travel_mode=request.travelData.travelMode,
            daily_plans=travel_plan.daily_plans,
            overview=travel_plan.overview
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成旅游计划失败: {str(e)}")