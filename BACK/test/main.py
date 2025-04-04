from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import uvicorn

app = FastAPI(title="智能旅游API测试")


# 数据模型
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
    travel_mode: Optional[str] = "walking"


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
    plan_id: str
    center_location: LocationRequest
    start_date: datetime
    end_date: datetime
    daily_plans: List[DailyPlan]
    overview: str


# API端点
@app.post("/api/travel/generate-plan", response_model=TravelPlanResponse)
async def generate_travel_plan(request: TravelPlanRequest):
    """生成旅游计划API"""
    try:
        # 检查是否为天安门
        if request.center_location.name and "天安门" in request.center_location.name:
            # 准备一个预设的天安门旅游计划
            start_date = request.start_date

            # 计算天数差
            days_diff = (request.end_date - request.start_date).days
            days_diff = max(1, min(days_diff, 3))  # 限制为1-3天

            # 预设旅游计划数据
            poi_data = [
                # 第一天景点
                [
                    {
                        "name": "天安门广场",
                        "address": "北京市东城区东长安街",
                        "latitude": 39.9054,
                        "longitude": 116.3976,
                        "description": "天安门广场是世界上最大的城市中心广场，也是中国的象征性建筑之一。这里有人民英雄纪念碑、毛主席纪念堂等著名景点。",
                        "recommended_duration": "1.5小时"
                    },
                    {
                        "name": "故宫博物院",
                        "address": "北京市东城区景山前街4号",
                        "latitude": 39.9163,
                        "longitude": 116.3972,
                        "description": "故宫是中国明清两代的皇家宫殿，世界上现存规模最大、保存最为完整的木质结构古建筑之一。内有珍贵文物藏品近百万件。",
                        "recommended_duration": "4小时"
                    },
                    {
                        "name": "景山公园",
                        "address": "北京市东城区景山前街44号",
                        "latitude": 39.9224,
                        "longitude": 116.3970,
                        "description": "景山公园位于故宫北侧，是一座人工山，登上山顶可俯瞰整个紫禁城全景，是拍摄故宫全景的最佳位置。",
                        "recommended_duration": "1小时"
                    }
                ],
                # 第二天景点
                [
                    {
                        "name": "天坛公园",
                        "address": "北京市东城区天坛内东里7号",
                        "latitude": 39.8822,
                        "longitude": 116.4066,
                        "description": "天坛是明清两代皇帝祭天的场所，也是现存中国古代规模最大、伦理等级最高的祭祀建筑群。",
                        "recommended_duration": "2.5小时"
                    },
                    {
                        "name": "前门大街",
                        "address": "北京市东城区前门东大街",
                        "latitude": 39.8994,
                        "longitude": 116.3923,
                        "description": "前门大街是北京市著名的传统商业街，保留了清末民初的街道风貌，有许多百年老店和特色小吃。",
                        "recommended_duration": "3小时"
                    },
                    {
                        "name": "大栅栏",
                        "address": "北京市西城区大栅栏街",
                        "latitude": 39.8951,
                        "longitude": 116.3867,
                        "description": "大栅栏是北京最古老的商业街区之一，拥有数百年历史，汇集了许多老字号商铺，是体验老北京文化的好去处。",
                        "recommended_duration": "2小时"
                    }
                ],
                # 第三天景点
                [
                    {
                        "name": "国家博物馆",
                        "address": "北京市东城区东长安街16号",
                        "latitude": 39.9053,
                        "longitude": 116.4012,
                        "description": "中国国家博物馆位于天安门广场东侧，是中国最大的博物馆，收藏了大量珍贵文物和艺术品，展示了中国悠久的历史和灿烂的文化。",
                        "recommended_duration": "3小时"
                    },
                    {
                        "name": "王府井步行街",
                        "address": "北京市东城区王府井大街",
                        "latitude": 39.9146,
                        "longitude": 116.4094,
                        "description": "王府井是北京最著名的商业街之一，有各种商场、专卖店和小吃街，是购物和品尝北京特色小吃的好去处。",
                        "recommended_duration": "3小时"
                    },
                    {
                        "name": "什刹海",
                        "address": "北京市西城区什刹海",
                        "latitude": 39.9402,
                        "longitude": 116.3849,
                        "description": "什刹海是北京著名的历史文化风景区，由前海、后海和西海组成，周围有许多胡同和四合院，是体验老北京风情的好地方。",
                        "recommended_duration": "2小时"
                    }
                ]
            ]

            # 创建旅游计划
            daily_plans = []
            for i in range(days_diff):
                current_date = start_date + timedelta(days=i)

                # 获取当天的景点
                day_index = min(i, len(poi_data) - 1)  # 避免超出范围
                pois = []

                for poi in poi_data[day_index]:
                    pois.append(PointOfInterest(
                        name=poi["name"],
                        address=poi["address"],
                        latitude=poi["latitude"],
                        longitude=poi["longitude"],
                        description=poi["description"],
                        recommended_duration=poi["recommended_duration"]
                    ))

                # 日计划描述
                day_descriptions = [
                    "今天的行程以天安门广场为起点，参观故宫博物院，然后在景山公园俯瞰紫禁城全景。建议上午前往天安门广场和故宫，下午游览景山公园。",
                    "今天的行程将带您体验更多北京的历史文化，从天坛公园开始，然后到前门大街和大栅栏感受老北京的商业文化。",
                    "最后一天以参观国家博物馆开始，然后前往王府井购物和品尝美食，最后在什刹海体验老北京的胡同文化。"
                ]

                daily_plans.append(DailyPlan(
                    date=current_date,
                    poi_list=pois,
                    description=day_descriptions[day_index]
                ))

            # 生成计划ID
            plan_id = str(uuid.uuid4())

            # 旅游计划概述，根据天数调整
            if days_diff == 1:
                overview = "这是一个以天安门为中心的一日游计划，您将参观天安门广场、故宫博物院和景山公园，体验北京深厚的历史文化底蕴。"
            elif days_diff == 2:
                overview = "这是一个为期两天的北京旅游计划，以天安门为中心。第一天参观天安门周边的故宫和景山公园，第二天前往天坛公园和前门大街，体验更多的历史文化景点。"
            else:
                overview = "这是一个为期三天的北京旅游计划，以天安门为中心。您将参观天安门广场、故宫博物院、天坛公园、前门大街等历史文化景点，以及王府井和什刹海等现代商业与传统文化交融的地区。"

            # 构建响应
            response = TravelPlanResponse(
                plan_id=plan_id,
                center_location=request.center_location,
                start_date=request.start_date,
                end_date=request.end_date,
                daily_plans=daily_plans,
                overview=overview
            )

            return response
        else:
            # 对于非天安门的请求，返回一个通用响应
            plan_id = str(uuid.uuid4())
            start_date = request.start_date

            # 创建一个简单的单日计划
            poi = PointOfInterest(
                name="旅游景点",
                address=f"{request.center_location.name or '未知地点'} 附近",
                latitude=request.center_location.latitude,
                longitude=request.center_location.longitude,
                description="这是一个示例景点描述，实际应用中会根据具体位置提供详细信息。",
                recommended_duration="2小时"
            )

            daily_plan = DailyPlan(
                date=start_date,
                poi_list=[poi],
                description="这是一个测试行程，实际应用中会提供更详细的行程安排。"
            )

            response = TravelPlanResponse(
                plan_id=plan_id,
                center_location=request.center_location,
                start_date=request.start_date,
                end_date=request.end_date,
                daily_plans=[daily_plan],
                overview="这是一个通用的测试旅游计划，实际应用中会根据具体位置和偏好生成更详细的计划。"
            )

            return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成旅游计划失败: {str(e)}")


# 添加一个根路径响应
@app.get("/")
async def root():
    return {"message": "智能旅游API测试服务已启动，访问 /docs 查看API文档"}


# 启动服务器的代码
if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)