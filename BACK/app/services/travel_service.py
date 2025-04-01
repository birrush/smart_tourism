from app.services.llm_service import LLMService
from app.models.schemas import LocationRequest, DailyPlan, PointOfInterest
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TravelPlan:
    """旅游计划数据类"""

    def __init__(self, daily_plans: List[DailyPlan], overview: str):
        self.daily_plans = daily_plans
        self.overview = overview


class TravelService:
    """旅游计划生成服务"""

    def __init__(self):
        self.llm_service = LLMService()

    async def generate_plan(
            self,
            center_location: LocationRequest,
            start_date: datetime,
            end_date: datetime,
            preferences: Optional[List[str]] = None,
            travel_mode: Optional[str] = "walking"
    ) -> TravelPlan:
        """
        生成旅游计划

        Args:
            center_location: 中心位置
            start_date: 开始日期
            end_date: 结束日期
            preferences: 偏好列表
            travel_mode: 出行方式

        Returns:
            生成的旅游计划
        """
        try:
            # 准备输入数据
            input_data = {
                "center_location": center_location.dict(),
                "start_date": start_date,
                "end_date": end_date,
                "preferences": preferences or [],
                "travel_mode": travel_mode
            }

            # 调用大模型服务
            llm_result = await self.llm_service.generate_travel_plan(input_data)

            # 转换大模型输出为应用数据格式
            daily_plans = []
            for day_plan in llm_result["daily_plans"]:
                # 转换日期字符串为datetime对象
                date = datetime.strptime(day_plan["date"], "%Y-%m-%d")

                # 转换POI列表
                poi_list = []
                for poi in day_plan["poi_list"]:
                    poi_obj = PointOfInterest(
                        name=poi["name"],
                        address=poi["address"],
                        latitude=poi["latitude"],
                        longitude=poi["longitude"],
                        description=poi["description"],
                        recommended_duration=poi.get("recommended_duration")
                    )
                    poi_list.append(poi_obj)

                # 创建日计划对象
                daily_plan = DailyPlan(
                    date=date,
                    poi_list=poi_list,
                    description=day_plan["description"]
                )
                daily_plans.append(daily_plan)

            # 创建旅游计划
            travel_plan = TravelPlan(
                daily_plans=daily_plans,
                overview=llm_result["overview"]
            )

            return travel_plan

        except Exception as e:
            logger.error(f"生成旅游计划失败: {str(e)}")
            raise