from typing import List, cast

from openai import OpenAI

from .types import LlmMessage, LlmResponse, ToolCall


class LlmClient:
    """
    封装与 OpenAI 兼容格式大语言模型的底层通信逻辑。
    """

    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        # 实例化 OpenAI 客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(
        self,
        messages: List[LlmMessage],
        tools_schema: List,
        temperature: float = 0.7,
    ) -> LlmResponse:
        """
        向 LLM API 发送请求并获取生成结果，包括模型生成的文本以及对应的工具调用请求。
        """
        try:
            # 发起聊天完成请求
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                tool_choice="auto",
                tools=tools_schema,
                temperature=temperature,
            )

            # 提取文本内容
            content = response.choices[0].message.content or ""
            tool_calls = cast(
                List[ToolCall], response.choices[0].message.tool_calls or []
            )

            # 提取停止原因，如工具调用 ('tool_calls') 还是正常停止 ('stop')
            finish_reason = response.choices[0].finish_reason

            return LlmResponse(
                content=content, tool_calls=tool_calls, finish_reason=finish_reason
            )
        except Exception as e:
            raise RuntimeError(f"LLM 请求失败: {e}")
