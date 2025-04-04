from pydantic_settings import BaseSettings
from typing import List
import os
# 修改前

# 修改后

from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "智能旅游"
    API_PREFIX: str = "/api"
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "False") == "True")

    # 跨域配置
    ALLOWED_ORIGINS: List[str] = ["*"]  # 在生产环境中应该限制为微信小程序域名

    # 微信小程序配置
    WX_APP_ID: str = Field(default="")
    WX_APP_SECRET: str = Field(default="")

    # 大模型API配置
    LLM_API_KEY: str = Field(default="")
    LLM_API_URL: str = Field(default="https://api.openai.com/v1/chat/completions")

    # 数据库配置（如果需要）
    DATABASE_URL: str = Field(default="")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


settings = Settings()