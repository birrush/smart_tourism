from fastapi import APIRouter
from app.api.endpoints import travel_plan
from app.core.config import settings

# 创建一个带有前缀的路由器
router = APIRouter(prefix=settings.API_PREFIX)

# 注册所有API端点路由
router.include_router(travel_plan.router, prefix="/travel", tags=["travel"])