from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    PROJECT_NAME: str = "智能旅游"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # 跨域配置
    ALLOWED_ORIGINS: List[str] = ["*"]  # 在生产环境中应该限制为微信小程序域名

    # 微信小程序配置
    WX_APP_ID: str = os.getenv("WX_APP_ID", "")
    WX_APP_SECRET: str = os.getenv("WX_APP_SECRET", "")

    # 大模型API配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")

    # 数据库配置（如果需要）
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()