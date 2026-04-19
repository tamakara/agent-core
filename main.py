import os

from dotenv import load_dotenv

from agent_core import Agent

# 加载 .env 文件中的环境变量配置
load_dotenv()

# 从环境变量中获取 LLM 相关的配置参数
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "")
MCP_SSE_URL = os.environ.get("MCP_SSE_URL", "http://localhost:8080/sse")
MCP_SSE_BEARER_TOKEN = os.environ.get("MCP_SSE_BEARER_TOKEN", "")

# 定义 Agent 的系统提示词，指导 Agent 的行为模式和任务约束
SYSTEM_PROMPT = """
- 如果问题需要实时或外部信息，优先调用对应工具，不要臆测。
- 可以连续调用多个工具来完成任务。
"""

# 唯一 MCP Server：SSE 网关

try:
    agent = Agent(
        llm_api_key=LLM_API_KEY,
        llm_base_url=LLM_BASE_URL,
        llm_model_name=LLM_MODEL_NAME,
        system_prompt=SYSTEM_PROMPT,
        mcp_sse_url=MCP_SSE_URL,
        mcp_sse_bearer_token=MCP_SSE_BEARER_TOKEN,
    )

    while True:
        user_prompt = input("请输入您的问题: ")
        response = agent.chat(user_input=user_prompt, max_turns=100)
        print(response)
except Exception as e:
    print(f"启动失败: {e}")
