from app.services.llm_service import LLMService
from app.models.schemas import ScenicSpot, DailyPlan, PointOfInterest
from typing import List, Dict, Any
import logging
from datetime import date, timedelta

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
            city: str,
            center_name: str,
            scenic_spots: List[ScenicSpot],
            travel_days: int,
            travel_mode: str
    ) -> TravelPlan:
        """
        生成旅游计划

        Args:
            city: 城市名称
            center_name: 中心位置名称
            scenic_spots: 用户选择的景点列表
            travel_days: 旅行天数
            travel_mode: 出行方式

        Returns:
            生成的旅游计划
        """
        try:
            # 准备输入数据
            input_data = {
                "city": city,
                "center_name": center_name,
                "scenic_spots": [spot.dict() for spot in scenic_spots] if scenic_spots else [],
                "travel_days": travel_days,
                "travel_mode": travel_mode
            }

            # 调用大模型服务
            llm_result = await self.llm_service.generate_travel_plan(input_data)

            # 转换大模型输出为应用数据格式
            daily_plans = []

            # 计算旅行的开始日期（今天开始）
            start_date = date.today()

            for day_plan in llm_result["daily_plans"]:
                # 计算当天日期
                current_date = start_date + timedelta(days=day_plan["day"] - 1)

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
                    day=day_plan["day"],
                    date=current_date,
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