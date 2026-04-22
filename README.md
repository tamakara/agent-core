# Agent Core

一个最小可用的 Python Agent 核心示例，基于 OpenAI 兼容接口 + MCP SSE Gateway 完成工具调用。

## 功能特性

- 多轮会话消息管理（`system / user / assistant / tool`）
- 通过 MCP SSE 网关动态发现远端工具（`list_tools`）
- 自动执行模型发起的工具调用并将结果回填上下文
- 支持会话清空（保留系统提示词）

## 目录结构

- `agent_core/agent_core.py`：`AgentCore` 主流程（对话循环、工具调度、会话重置）
- `agent_core/tool_registry.py`：MCP 工具发现、schema 转换、工具调用
- `agent_core/messages_storage.py`：会话消息存储
- `agent_core/llm_client.py`：LLM 客户端封装
- `agent_core/types.py`：类型定义
- `main.py`：可运行示例（从环境变量读取 LLM + MCP 配置）

## 前置要求

- Python 3.10+
- Docker Desktop 已启动
- 已安装 Docker MCP Toolkit（可用 `docker mcp --help` 验证）
- 本地已配置至少一个可用的 MCP Server（由 Docker MCP 管理）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

参考 `.env.example`：

```env
LLM_API_KEY=sk-xxxxxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-5.4
MCP_SSE_URL=http://localhost:8080/sse
MCP_SSE_BEARER_TOKEN=xxxxxx
```

## 快速开始

### 1) 启动 MCP Gateway（先做）

在单独终端中运行：

```bash
docker mcp gateway run --transport sse --port 8080
```

如果你本机安装了 `mcp` 独立命令，也可以使用：

```bash
mcp gateway run --transport sse --port 8080
```

### 2) 启动 Agent

```bash
python main.py
```

启动后可直接输入问题，例如：

```text
帮我查下今天上海天气，并给我穿衣建议
```

## 示例代码

```python
from agent_core import AgentCore

agent = AgentCore(
    llm_api_key="your_key",
    llm_base_url="https://api.openai.com/v1",
    llm_model_name="gpt-5.4",
    system_prompt="你是一个有帮助的助手",
    mcp_sse_url="http://localhost:8080/sse",
    mcp_sse_bearer_token="",
)

answer = agent.chat("请帮我处理这个问题")
print(answer)
```

## 常见问题

- `mcp: command not found`
  - 优先使用 `docker mcp ...` 命令，或检查 `mcp` 是否已加入 PATH。
- `Docker Desktop is not running`
  - 先启动 Docker Desktop，再执行 gateway 命令。
- `启动失败: 连接 MCP SSE 服务失败`
  - 确认网关正在运行、`MCP_SSE_URL` 正确，且网关后面有可用 MCP Server。

## 注意事项

- `chat()` 在单次工具调用异常时会打印错误并继续后续流程。
- 达到 `max_turns` 仍未完成会抛出 `RuntimeError`。
- 当前包仅对外导出 `AgentCore`。
