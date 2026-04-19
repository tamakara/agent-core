import json
from inspect import getdoc
from typing import Any

from pydantic.experimental.arguments_schema import generate_arguments_schema
from pydantic.json_schema import GenerateJsonSchema

from agent_core.messages_storage import MessagesStorage

from .llm_client import LlmClient


def _build_function_tool_schema(tool_name: str, tool: Any) -> dict[str, Any]:
    """
    根据 Python 函数自动生成 OpenAI Function Calling 格式的 schema。

    :param tool_name: 工具名称。
    :param tool: 实际的工具函数对象。
    :return: 包含该工具参数描述的 JSON schema 字典。
    """
    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": getdoc(tool) or "",
            "parameters": GenerateJsonSchema().generate(
                generate_arguments_schema(tool)
            ),
        },
    }


class Agent:
    """
    智能体类，负责维护对话历史、管理工具调用流程与大模型交互。
    """

    def __init__(
        self,
        llm_client: LlmClient,
        tools: dict,
        system_prompt: str,
        messages_storage: MessagesStorage,
    ):
        self.llm_client = llm_client
        self.tool_functions = tools
        # 预先生成所有工具的 schema 数据，用于后续传给模型
        self.tools_schema = [
            _build_function_tool_schema(tool_name, tool)
            for tool_name, tool in tools.items()
        ]
        # 初始化消息记录，设置系统提示词
        self.messages_storage = messages_storage
        self.messages_storage.add_system_message(system_prompt)

    def chat(self, user_input: str, max_turns: int = 10) -> str:
        """
        开始对话并执行自动的工具调用逻辑直到获得最终结果。

        :param user_input: 用户的自然语言输入。
        :param max_turns: 最大对话轮数，防止陷入无限循环调用。
        :return: 模型的最终回复。
        """
        self.messages_storage.add_user_message(user_input)

        # 进入对话循环，模型可能会多轮调用工具直到完成任务或达到最大轮数限制
        for _ in range(max_turns):
            # 获取当前对话历史并传给模型，模型会根据历史消息决定是否调用工具
            llm_response = self.llm_client.generate(
                messages=self.messages_storage.get_messages(),
                tools_schema=self.tools_schema,
            )
            # 记录模型的回复和工具调用信息
            self.messages_storage.add_assistant_message(
                llm_response.content, llm_response.tool_calls
            )

            # 如果模型回复中没有工具调用了，说明对话已经完成，可以直接返回结果了
            if llm_response.finish_reason != "tool_calls":
                if llm_response.finish_reason == "stop":
                    return llm_response.content
                else:
                    raise RuntimeError(
                        f"LLM response ended with unexpected reason: {llm_response.finish_reason}"
                    )

            for tool_call in llm_response.tool_calls:
                tool_call_id = tool_call.id
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments

                try:
                    # 解析工具参数，支持已经解析好的字典或是 JSON 字符串
                    tool_args = (
                        json.loads(tool_args_str)
                        if isinstance(tool_args_str, str)
                        else tool_args_str
                    )
                    # 执行工具函数并获取结果，工具函数的参数需要与模型传来的参数完全匹配
                    tool_call_result = str(self.tool_functions[tool_name](**tool_args))
                except Exception as e:
                    continue

                # 记录工具执行的结果以备下一轮模型推理
                self.messages_storage.add_tool_message(
                    tool_name, tool_call_result, tool_call_id
                )
        raise RuntimeError(
            f"Agent failed to complete the task within {max_turns} turns of interaction."
        )
