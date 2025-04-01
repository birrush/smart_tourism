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
    """根据中心位置和计划时间生成旅游计划"""
    try:
        # 调用旅游服务生成计划
        travel_plan = await travel_service.generate_plan(
            center_location=request.center_location,
            start_date=request.start_date,
            end_date=request.end_date,
            preferences=request.preferences,
            travel_mode=request.travel_mode
        )

        # 生成计划ID
        plan_id = str(uuid.uuid4())

        # 构建响应
        response = TravelPlanResponse(
            plan_id=plan_id,
            center_location=request.center_location,
            start_date=request.start_date,
            end_date=request.end_date,
            daily_plans=travel_plan.daily_plans,
            overview=travel_plan.overview
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成旅游计划失败: {str(e)}")