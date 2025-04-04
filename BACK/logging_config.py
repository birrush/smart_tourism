import logging
import os
from logging.handlers import RotatingFileHandler

# 确保logs目录存在
os.makedirs("logs", exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("logs/app.log", maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)