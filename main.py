import os
import re

from dotenv import load_dotenv

from agent_core import Agent

# 加载 .env 文件中的环境变量配置
load_dotenv()

# 从环境变量中获取 LLM 相关的配置参数
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "")

# 定义 Agent 的系统提示词，指导 Agent 的行为模式和任务约束
AGENT_SYSTEM_PROMPT = """
- 如果问题需要实时或外部信息，优先调用对应工具，不要臆测。
- 可以连续调用多个工具来完成任务。
- 在拿到足够信息后，直接给出简洁、清晰、对用户有帮助的最终答案。
"""


# 供 LLM Function Calling 使用的数学计算工具
def calculate(expression: str) -> str:
    """
    计算数学表达式并返回结果字符串。

    该函数会作为 tool 提供给 LLM。请传入纯数学表达式，不要包含变量、函数名
    或其他非数学字符。

    参数:
        expression: 待计算表达式。支持数字、空白、小数点、括号以及
            + - * / // % ** 运算符。

    返回:
        成功时返回计算结果字符串；失败时返回以“错误:”开头的错误信息。
    """
    try:
        expr = expression.strip()
        if not expr:
            return "错误:表达式不能为空"

        if len(expr) > 100:
            return "错误:表达式过长"

        # 仅允许数字、小数点、空白、括号及数学运算符。
        if not re.fullmatch(r"[\d\s+\-*/%().]+", expr):
            return "错误:表达式包含非法字符"

        value = eval(expr, {"__builtins__": {}}, {})
        if not isinstance(value, (int, float)):
            return "错误:表达式结果不是数字"

        return str(value)
    except Exception as e:
        return f"错误:无法计算表达式 - {e}"


# 将所有工具函数放入一个字典，方便后续调用
AVAILABLE_TOOLS = {
    "calculate": calculate,
}

# 初始化 Agent，传入客户端、功能工具和系统提示词
agent = Agent(
    llm_api_key=LLM_API_KEY,
    llm_base_url=LLM_BASE_URL,
    llm_model_name=LLM_MODEL_NAME,
    system_prompt=AGENT_SYSTEM_PROMPT,
    tools=AVAILABLE_TOOLS,
)

while True:
    # 模拟用户的提问
    user_prompt = input("请输入您的问题: ")

    # 启动与 Agent 的对话，执行推理和工具调用流程
    response = agent.chat(user_input=user_prompt, max_turns=100)

    # 打印最终的回答结果
    print(response)
