import json
from typing import Any, Callable

from .llm_client import LlmClient
from .messages_storage import MessagesStorage
from .tool_registry import ToolRegistry


class Agent:
    """
    智能体类，负责维护对话历史、管理工具调用流程与大模型交互。
    """

    def __init__(
        self,
        llm_model_name: str,
        llm_api_key: str,
        llm_base_url: str,
        system_prompt: str,
        tools: dict[str, Callable[..., Any]] = {},
    ):
        # 初始化 LLM 客户端
        self._llm_client = LlmClient(
            model=llm_model_name, api_key=llm_api_key, base_url=llm_base_url
        )

        # 保存系统提示词，便于会话清空后恢复初始上下文
        self._system_prompt = system_prompt

        # 初始化消息存储对象，设置系统提示词
        self._messages_storage = MessagesStorage()
        self._messages_storage.add_system_message(self._system_prompt)

        # 初始化工具注册表
        self._tool_registry = ToolRegistry()
        self._tool_registry.register_tools(tools)

    def chat(self, user_input: str, max_turns: int = 10) -> str:
        """
        开始对话并执行自动的工具调用逻辑直到获得最终结果。

        :param user_input: 用户的自然语言输入。
        :param max_turns: 最大对话轮数，防止陷入无限循环调用。
        :return: 模型的最终回复。
        """
        self._messages_storage.add_user_message(user_input)

        # 进入对话循环，模型可能会多轮调用工具直到完成任务或达到最大轮数限制
        for _ in range(max_turns):
            # 每轮读取最新的工具 schema，支持运行时注册新工具
            llm_response = self._llm_client.generate(
                messages=self._messages_storage.get_messages(),
                tools_schema=self._tool_registry.get_tools_schema(),
            )
            # 记录模型的回复和工具调用信息
            self._messages_storage.add_assistant_message(
                llm_response.content, llm_response.tool_calls
            )

            # 如果模型回复中没有工具调用了，说明对话已经完成，可以直接返回结果了
            if llm_response.finish_reason != "tool_calls":
                if llm_response.finish_reason == "stop":
                    return llm_response.content
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
                    tool_call_result = self._tool_registry.call_tool(
                        tool_name=tool_name, tool_args=tool_args
                    )
                except Exception as e:
                    print(f"Error occurred while calling tool '{tool_name}': {e}")
                    continue

                # 记录工具执行的结果以备下一轮模型推理
                self._messages_storage.add_tool_message(
                    tool_name, tool_call_result, tool_call_id
                )

        raise RuntimeError(
            f"Agent failed to complete the task within {max_turns} turns of interaction."
        )

    def register_tool(self, tool_name: str, tool: Callable[..., Any]) -> None:
        """注册单个工具函数。"""
        self._tool_registry.register_tool(tool_name=tool_name, tool=tool)

    def register_tools(self, tools: dict[str, Callable[..., Any]]) -> None:
        """批量注册工具函数。"""
        self._tool_registry.register_tools(tools=tools)

    def clear_session(self) -> None:
        """
        清空当前会话历史，并恢复初始系统提示词。
        已注册工具会保留。
        """
        self._messages_storage.clear()
        self._messages_storage.add_system_message(self._system_prompt)
