import httpx
from app.core.config import settings
from typing import Dict, Any
import json
import logging

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
            input_data: 包含位置和日期信息的字典

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
        location = input_data["center_location"]
        location_str = f"{location['name'] or ''} ({location['latitude']}, {location['longitude']})"

        start_date = input_data["start_date"].strftime("%Y-%m-%d")
        end_date = input_data["end_date"].strftime("%Y-%m-%d")

        preferences = "、".join(input_data.get("preferences", [])) if input_data.get("preferences") else "无特殊偏好"

        prompt = f"""
        请为我生成一份详细的旅游计划:

        中心位置: {location_str}
        地址: {location.get('address', '未提供')}
        开始日期: {start_date}
        结束日期: {end_date}
        偏好: {preferences}
        出行方式: {input_data.get('travel_mode', '步行')}

        请提供以下内容:
        1. 旅游计划概述
        2. 每天的详细行程，包括:
           - 推荐景点的名称、地址、坐标、描述和推荐游玩时长
           - 景点之间的最佳路线
           - 每天的用餐建议
        3. 每个景点的简要介绍

        请以JSON格式返回，格式如下:
        ```json
        {
        "overview": "旅游计划概述",
          "daily_plans": [
            {
        "date": "YYYY-MM-DD",
              "description": "当天概述",
              "poi_list": [
                {
        "name": "景点名称",
                  "address": "景点地址",
                  "latitude": 123.456,
                  "longitude": 78.910,
                  "description": "景点描述",
                  "recommended_duration": "2小时"
                }
              ]
            }
          ]
        }
        ```
        请确保输出是有效的JSON格式。
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