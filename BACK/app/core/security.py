from fastapi import Depends, HTTPException, Header, Request
from app.core.config import settings
import hashlib
import time
from typing import Optional


async def verify_wx_request(
        request: Request,
        signature: Optional[str] = Header(None),
        timestamp: Optional[str] = Header(None),
        nonce: Optional[str] = Header(None)
) -> bool:
    """
    验证请求是否来自微信小程序
    简化版，实际中需要使用适当的安全机制
    """
    # 在开发环境中跳过验证
    if settings.DEBUG:
        return True

    # 实际生产中应该实现真正的请求验证
    # 可以使用微信小程序的登录接口获取的session_key验证
    # 或者使用自定义的token系统

    # 这里只是示例，真实场景需要根据微信小程序开发文档实现
    if not all([signature, timestamp, nonce]):
        raise HTTPException(status_code=401, detail="未授权访问")

    return True