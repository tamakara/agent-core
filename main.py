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
SYSTEM_PROMPT = """
- 如果问题需要实时或外部信息，优先调用对应工具，不要臆测。
- 可以连续调用多个工具来完成任务。
"""

# 将所有工具函数放入一个字典，方便后续调用
MCP_SERVERS = ['http://localhost:8001', 'http://localhost:8002']

# 初始化 Agent，传入客户端、功能工具和系统提示词
agent = Agent(
    llm_api_key=LLM_API_KEY,
    llm_base_url=LLM_BASE_URL,
    llm_model_name=LLM_MODEL_NAME,
    system_prompt=SYSTEM_PROMPT,
    mcp_servers=MCP_SERVERS,
)

while True:
    # 模拟用户的提问
    user_prompt = input("请输入您的问题: ")

    # 启动与 Agent 的对话，执行推理和工具调用流程
    response = agent.chat(user_input=user_prompt, max_turns=100)

    # 打印最终的回答结果
    print(response)
