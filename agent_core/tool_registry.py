from inspect import getdoc
from typing import Any, Callable, Dict, List

from pydantic.experimental.arguments_schema import generate_arguments_schema
from pydantic.json_schema import GenerateJsonSchema


class ToolRegistry:
    """
    统一管理可被 LLM 调用的工具函数及其 OpenAI Function Calling schema。
    """

    def __init__(self):
        # 工具名 -> 可调用函数
        self.tool_functions: Dict[str, Callable[..., Any]] = {}
        # 基于当前工具集合生成的 schema 缓存
        self.tools_schema: List[Dict[str, Any]] = []

    def register_tool(self, tool_name: str, tool: Callable[..., Any]) -> None:
        """
        注册单个工具；同名工具会被覆盖。
        """
        self.tool_functions[tool_name] = tool
        self._refresh_tools_schema()

    def register_tools(self, tools: Dict[str, Callable[..., Any]]) -> None:
        """
        批量注册工具；同名工具会被覆盖。
        """
        self.tool_functions.update(tools)
        self._refresh_tools_schema()

    def _refresh_tools_schema(self) -> None:
        """
        每次注册后重建 schema，保证传给模型的工具定义与当前注册表一致。
        """
        self.tools_schema = [
            self._build_function_tool_schema(tool_name, tool)
            for tool_name, tool in self.tool_functions.items()
        ]

    def _build_function_tool_schema(
        self, tool_name: str, tool: Callable[..., Any]
    ) -> Dict[str, Any]:
        """
        根据 Python 函数签名与文档生成单个工具 schema。
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

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        获取当前可用工具的 schema 列表。
        """
        return self.tools_schema

    def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """
        按工具名执行工具，并将结果统一转为字符串返回。
        """
        return str(self.tool_functions[tool_name](**tool_args))
