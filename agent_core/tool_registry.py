from inspect import getdoc
from typing import Any, Callable

from pydantic.experimental.arguments_schema import generate_arguments_schema
from pydantic.json_schema import GenerateJsonSchema


class ToolRegistry:
    def __init__(self):
        self.tool_functions: dict[str, Callable[..., Any]] = {}
        self.tools_schema: list[dict[str, Any]] = []

    def register_tool(self, tool_name: str, tool: Callable[..., Any]) -> None:
        self.tool_functions[tool_name] = tool
        self._refresh_tools_schema()

    def register_tools(self, tools: dict[str, Callable[..., Any]]) -> None:
        self.tool_functions.update(tools)
        self._refresh_tools_schema()

    def _refresh_tools_schema(self) -> None:
        self.tools_schema = [
            self._build_function_tool_schema(tool_name, tool)
            for tool_name, tool in self.tool_functions.items()
        ]

    def _build_function_tool_schema(
        self, tool_name: str, tool: Callable[..., Any]
    ) -> dict[str, Any]:
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

    def get_tools_schema(self) -> list[dict[str, Any]]:
        return self.tools_schema

    def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> str:
        return str(self.tool_functions[tool_name](**tool_args))
