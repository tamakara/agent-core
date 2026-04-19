from typing import List, cast

from .types import LlmMessage, ToolCall


class MessagesStorage:
    """
    管理对话消息历史，统一封装不同角色消息的入库逻辑。
    """

    def __init__(self):
        # 按时间顺序保存完整对话上下文（system/user/assistant/tool）
        self.messages: List[LlmMessage] = []

    def add_system_message(self, content: str) -> None:
        """
        添加 system 消息，用于约束模型行为。
        """
        self.messages.append({"role": "system", "content": content})

    def add_assistant_message(self, content: str, tool_calls: List[ToolCall]) -> None:
        """
        添加 assistant 消息，并记录该轮模型提出的工具调用信息。
        """
        self.messages.append(
            cast(
                LlmMessage,
                {"role": "assistant", "content": content, "tool_calls": tool_calls},
            )
        )

    def add_user_message(self, content: str) -> None:
        """
        添加 user 消息。
        """
        self.messages.append({"role": "user", "content": content})

    def add_tool_message(self, name: str, content: str, tool_call_id: str) -> None:
        """
        添加 tool 消息，将工具执行结果回填给模型继续推理。
        """
        self.messages.append(
            cast(
                LlmMessage,
                {
                    "role": "tool",
                    "name": name,
                    "content": content,
                    "tool_call_id": tool_call_id,
                },
            )
        )

    def get_messages(self) -> List[LlmMessage]:
        """
        获取当前完整消息历史（按引用返回，调用方可直接读取）。
        """
        return self.messages

    def clear(self) -> None:
        """
        清空当前会话消息历史。
        """
        self.messages.clear()
