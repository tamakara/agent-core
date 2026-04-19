# Agent Core

一个最小可用的 Python Agent 核心示例，支持 OpenAI 兼容接口与 Function Calling 工具调用。

## 功能特性

- 多轮会话消息管理（system / user / assistant / tool）
- 基于函数签名自动生成工具 schema
- 模型工具调用结果自动执行并回填上下文
- 支持运行时注册工具
- 支持清空会话并保留系统提示词与已注册工具

## 目录结构

- `agent_core/agent.py`：`Agent` 主流程（对话循环、工具调度、会话重置）
- `agent_core/tool_registry.py`：工具注册与 schema 生成
- `agent_core/messages_storage.py`：会话消息存储
- `agent_core/llm_client.py`：LLM 客户端封装
- `agent_core/types.py`：类型定义
- `main.py`：可运行示例（内置 `calculate` 工具）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

可参考 `.env.example`：

```env
LLM_API_KEY=sk-xxxxxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-5.4
```

## 快速开始

```bash
python main.py
```

启动后可直接输入问题，例如：

```text
帮我计算 (12.5 + 3) * 2 - 4 / 2
```

## Agent 使用方式

### 1) 构造时传入工具

```python
from agent_core import Agent

agent = Agent(
    llm_api_key="your_key",
    llm_base_url="https://api.openai.com/v1",
    llm_model_name="gpt-5.4",
    system_prompt="你是一个有帮助的助手",
    tools={"calculate": calculate},
)
```

### 2) 构造后动态注册工具

```python
agent = Agent(
    llm_api_key="your_key",
    llm_base_url="https://api.openai.com/v1",
    llm_model_name="gpt-5.4",
    system_prompt="你是一个有帮助的助手",
)
agent.register_tool("calculate", calculate)
# 或批量：
# agent.register_tools({"calculate": calculate, "search": search})
```

### 3) 对话与清空会话

```python
answer = agent.chat("2+2 等于多少？")
agent.clear_session()  # 清空历史消息，保留 system prompt 和已注册工具
```

## 工具函数约定

- 工具函数应有清晰的参数类型注解（用于生成 schema）
- 建议写 docstring（用于工具描述）
- 工具返回值会被统一转为字符串回填给模型

## 当前示例工具（main.py）

`calculate(expression: str) -> str`

- 支持数字、空白、小数点、括号、`+ - * / // % **`
- 对非法输入返回错误信息字符串

## 注意事项

- `chat()` 在工具执行异常时会跳过该次工具调用并继续流程
- 达到 `max_turns` 仍未完成会抛出 `RuntimeError`
- 当前包仅对外导出 `Agent`
