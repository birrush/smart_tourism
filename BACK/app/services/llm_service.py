from openai import OpenAI
from app.core.config import settings
from typing import Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)


class LLMService:
    """大模型API调用服务"""

    def __init__(self):
        self.api_key = "*******"  # 从配置中获取 API Key
        self.api_url = "https://api.moonshot.cn/v1"  # Kimi API的基础URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

    async def generate_travel_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用Kimi的API生成旅游计划

        Args:
            input_data: 包含位置和旅行天数信息的字典

        Returns:
            生成的旅游计划字典
        """
        try:
            # 构建提示词
            prompt = self._build_travel_prompt(input_data)

            # 调用Kimi API的completion请求
            completion = self.client.chat.completions.create(
                model="moonshot-v1-auto",  # 选择合适的模型
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的旅游规划助手，能够合理的帮助用户规划具体的旅游方案。你的回答必须是纯JSON格式，不要添加任何额外的解释文字。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            # 通过 API 获得模型回复消息
            result = completion.choices[0].message.content  # 直接获取字符串内容
            travel_plan = self._parse_llm_response(result)  # 传入字符串

            return travel_plan

        except Exception as e:
            logger.error(f"调用Kimi API失败: {str(e)}")
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
                # 使用字典访问值并确保正确的 JSON 格式
                scenic_spots_text += f"{i}. {spot['name']}, 地址: {spot['address']}, 坐标: ({spot['latitude']}, {spot['longitude']})\n"

        # 构建提示词
        prompt = f"""
        请为我生成一份详细的旅游计划，遵循以下要求：

        城市: {city}
        中心位置: {center_name}
        旅行天数: {travel_days}天
        出行方式: {travel_mode}
        {scenic_spots_text}

        请根据以下要求制定一个合理的旅游行程:
        1. 以中心位置为基础，规划{travel_days}天的行程
        2. 考虑到用户的出行方式是{travel_mode}，规划合理的游览路线
        3. 每天安排2-4个景点，考虑景点之间的距离和游览时间
        4. 若用户已选择景点，请确保将这些景点合理地融入到行程中

        你必须严格按照下面的JSON格式返回完整的旅游计划，不要添加任何额外的解释文本：

        {{
          "overview": "旅游计划概述",
          "daily_plans": [
            {{
              "day": 1,
              "description": "第一天概述",
              "poi_list": [
                {{
                  "name": "景点名称",
                  "address": "景点地址",
                  "latitude": 39.123456,
                  "longitude": 116.123456,
                  "description": "景点描述",
                  "recommended_duration": "2小时"
                }}
              ]
            }}
          ]
        }}

        请确保：
        1. 返回的是纯JSON格式，不包含```json标记或任何说明文字
        2. 所有JSON语法必须准确无误（如引号、逗号等）
        3. 坐标信息尽量准确
        4. 只返回这个JSON对象，不要有任何其他内容
        """

        return prompt

    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """解析并处理大模型的响应，能够处理各种可能的格式问题"""
        try:
            # 记录原始响应以便调试
            logger.debug(f"原始响应内容: {content}")

            # 1. 首先尝试直接解析整个内容（如果是纯JSON）
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.debug("直接解析失败，尝试提取JSON部分")

            # 2. 尝试查找JSON代码块
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                try:
                    return json.loads(json_match.group(1).strip())
                except json.JSONDecodeError:
                    logger.debug("从代码块提取的JSON解析失败")

            # 3. 尝试寻找大括号对
            json_start = content.find("{")
            json_end = content.rfind("}")

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = content[json_start:json_end + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.debug("从大括号提取的JSON解析失败")

            # 4. 尝试清理和修复常见问题后再解析
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end + 1]

                # 尝试修复常见JSON语法错误
                # 替换单引号为双引号（但不替换已转义的引号）
                fixed_json = re.sub(r"(?<!\\)'", '"', json_str)

                # 修复错误的转义序列
                fixed_json = fixed_json.replace('\\"', '"')
                fixed_json = fixed_json.replace('\\\'', "'")

                # 修复重复的逗号
                fixed_json = re.sub(r',\s*,', ',', fixed_json)
                fixed_json = re.sub(r',\s*}', '}', fixed_json)
                fixed_json = re.sub(r',\s*]', ']', fixed_json)

                # 修复缺失的逗号
                fixed_json = re.sub(r'"\s*{', '",{', fixed_json)
                fixed_json = re.sub(r'}\s*"', '},"', fixed_json)

                # 替换误写的分号为逗号
                fixed_json = fixed_json.replace(';', ',')

                logger.debug(f"修复后的JSON: {fixed_json}")

                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError as e:
                    logger.error(f"修复后的JSON仍然解析失败: {str(e)}")

                    # 尝试进一步分析错误位置
                    error_msg = str(e)
                    line_match = re.search(r'line (\d+)', error_msg)
                    col_match = re.search(r'column (\d+)', error_msg)

                    if line_match and col_match:
                        line = int(line_match.group(1))
                        col = int(col_match.group(1))

                        # 获取错误行及其上下文
                        lines = fixed_json.split('\n')
                        error_line = lines[line - 1] if line <= len(lines) else ""
                        error_context = f"问题行: {error_line}\n"
                        error_context += f"位置: {' ' * (col - 1)}^"

                        logger.error(f"JSON错误位置: {error_context}")

            # 5. 如果所有方法都失败，则进行更激进的修复尝试
            try:
                # 尝试使用正则表达式提取JSON结构
                # 此方法风险较高，可能会产生与原意不符的结果
                overview_match = re.search(r'"overview"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"', content)
                overview = overview_match.group(1) if overview_match else "未能提取旅游计划概述"

                # 提取daily_plans部分
                daily_plans = []
                day_matches = re.finditer(r'"day"\s*:\s*(\d+)', content)

                for day_match in day_matches:
                    day_num = int(day_match.group(1))
                    desc_match = re.search(fr'"day"\s*:\s*{day_num}[^{{]*"description"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"',
                                           content)
                    description = desc_match.group(1) if desc_match else f"第{day_num}天行程"

                    pois = []
                    poi_matches = re.finditer(fr'"day"\s*:\s*{day_num}[^{{]*"poi_list"\s*:\s*\[(.*?)\]', content,
                                              re.DOTALL)

                    for poi_match in poi_matches:
                        poi_block = poi_match.group(1)
                        for poi_item in re.finditer(r'{(.*?)}', poi_block, re.DOTALL):
                            poi_content = poi_item.group(1)
                            name_match = re.search(r'"name"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"', poi_content)
                            name = name_match.group(1) if name_match else "景点"

                            address_match = re.search(r'"address"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"', poi_content)
                            address = address_match.group(1) if address_match else "地址未提供"

                            lat_match = re.search(r'"latitude"\s*:\s*([\d\.]+)', poi_content)
                            lat = float(lat_match.group(1)) if lat_match else 0.0

                            lng_match = re.search(r'"longitude"\s*:\s*([\d\.]+)', poi_content)
                            lng = float(lng_match.group(1)) if lng_match else 0.0

                            desc_match = re.search(r'"description"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"', poi_content)
                            desc = desc_match.group(1) if desc_match else "没有描述"

                            dur_match = re.search(r'"recommended_duration"\s*:\s*"([^"\\]*(\\.[^"\\]*)*)"', poi_content)
                            duration = dur_match.group(1) if dur_match else "1小时"

                            pois.append({
                                "name": name,
                                "address": address,
                                "latitude": lat,
                                "longitude": lng,
                                "description": desc,
                                "recommended_duration": duration
                            })

                    daily_plans.append({
                        "day": day_num,
                        "description": description,
                        "poi_list": pois
                    })

                if not daily_plans:
                    raise ValueError("无法提取日程计划")

                # 组装最终的旅游计划
                travel_plan = {
                    "overview": overview,
                    "daily_plans": daily_plans
                }

                logger.warning("使用正则表达式提取了旅游计划，可能不完整或有误")
                return travel_plan

            except Exception as regex_error:
                logger.error(f"正则表达式提取失败: {str(regex_error)}")

            # 如果所有方法都失败，抛出异常
            raise ValueError("无法解析大模型响应为有效的旅游计划")

        except Exception as e:
            logger.error(f"解析大模型响应失败: {str(e)}")
            raise ValueError(f"无法解析大模型响应为有效的旅游计划: {str(e)}")