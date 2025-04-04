import httpx
from app.core.config import settings
from typing import Dict, Any, List
import json
import logging
from app.models.schemas import ScenicSpot

logger = logging.getLogger(__name__)


class LLMService:
    """大模型API调用服务"""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.api_url = settings.LLM_API_URL
        self.client = httpx.AsyncClient(timeout=60.0)  # 设置较长的超时时间

    async def generate_travel_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用大模型API生成旅游计划

        Args:
            input_data: 包含位置和旅行天数信息的字典

        Returns:
            生成的旅游计划字典
        """
        try:
            # 构建提示词
            prompt = self._build_travel_prompt(input_data)

            # 调用API的请求体
            payload = {
                "messages": [
                    {"role": "system",
                     "content": "你是一个专业的旅游规划助手，可以根据地点和时间提供详细的旅游行程计划。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }

            # 设置API请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # 发送请求到大模型API
            response = await self.client.post(
                self.api_url,
                json=payload,
                headers=headers
            )

            # 检查响应状态
            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 处理大模型输出，转换为结构化数据
            travel_plan = self._parse_llm_response(result)

            return travel_plan

        except Exception as e:
            logger.error(f"调用大模型API失败: {str(e)}")
            raise

    def _build_travel_prompt(self, input_data: Dict[str, Any]) -> str:
        """构建旅游计划的提示词"""
        city = input_data["city"]
        center_name = input_data["center_name"]
        travel_days = input_data["travel_days"]
        travel_mode = input_data["travel_mode"]

        # 处理已有的景点列表
        scenic_spots_text = ""
        if input_data.get("scenic_spots") and len(input_data["scenic_spots"]) > 0:
            scenic_spots_text = "用户已选择的景点:\n"
            for i, spot in enumerate(input_data["scenic_spots"], 1):
                scenic_spots_text += f"{i}. {spot.name}, 地址: {spot.address}, 坐标: ({spot.latitude}, {spot.longitude})\n"

        prompt = f"""
        请为我生成一份详细的旅游计划:

        城市: {city}
        中心位置: {center_name}
        旅行天数: {travel_days}天
        出行方式: {travel_mode}
        要参观的景点: {scenic_spots_text}

        请根据以下要求制定一个合理的旅游行程:
        1. 以中心位置为基础，规划{travel_days}天的行程
        2. 考虑到用户的出行方式是{travel_mode}，规划合理的游览路线
        3. 每天安排2-4个景点，考虑景点之间的距离和游览时间
        4. 若用户已选择景点，请确保将这些景点合理地融入到行程中

        请提供以下内容:
        1. 旅游计划概述
        2. 每天的详细行程，包括:
           推荐景点的名称、地址、大致坐标、描述和推荐游玩时长
           景点之间的最佳游览顺序
           每天的用餐建议

        请以JSON格式返回，格式如下:
        ```json
        {
        "overview": "旅游计划概述",
          "daily_plans": [
            {
        "day": 1,
              "description": "第一天概述",
              "poi_list": [
                {
        "name": "景点名称",
                  "address": "景点地址",
                  "latitude": 39.123456,
                  "longitude": 116.123456,
                  "description": "景点描述",
                  "recommended_duration": "2小时"
                }
              ]
            }
          ]
        }
        ```
        请确保输出是有效的JSON格式，并且坐标信息尽量准确。
        """

        return prompt

    def _parse_llm_response(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """解析并处理大模型的响应"""
        try:
            # 从大模型响应中提取内容
            content = llm_response["choices"][0]["message"]["content"]

            # 从内容中提取JSON部分
            json_start = content.find("{")
            json_end = content.rfind("}")

            if json_start == -1 or json_end == -1:
                raise ValueError("响应中未找到有效的JSON格式")

            json_str = content[json_start:json_end + 1]

            # 解析JSON
            travel_plan = json.loads(json_str)

            return travel_plan

        except Exception as e:
            logger.error(f"解析大模型响应失败: {str(e)}")
            logger.debug(f"原始响应: {llm_response}")
            raise ValueError("无法解析大模型响应为有效的旅游计划")