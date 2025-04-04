# main.py - 主入口文件

# 首先导入日志配置，确保它在所有其他导入之前执行
import logging_config

# 然后导入其他必要的模块
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
import logging

# 获取logger实例
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="智能旅游微信小程序后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info(f"应用启动: {settings.PROJECT_NAME}")
    logger.info(f"调试模式: {settings.DEBUG}")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"应用关闭: {settings.PROJECT_NAME}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)