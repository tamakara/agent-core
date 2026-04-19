# Agent Core

一个最小可用的通用 Agent 核心示例。

当前示例只提供一个工具：`calculate(expression: str)`，用于数学表达式计算。

## 功能

- 多轮消息管理
- OpenAI 兼容接口调用
- Function Calling 工具自动注册
- 工具执行结果自动回填

## 项目结构

- `agent_core/`: 核心包
- `agent_core/agent.py`: Agent 调用循环与工具执行
- `agent_core/llm_client.py`: LLM 客户端封装
- `main.py`: 最小示例入口（仅 calculate 工具）
- `requirements.txt`: 依赖

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```env
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o
```

### 3. 运行

```bash
python main.py
```

程序会提示输入问题，例如：

```text
帮我计算 (12.5 + 3) * 2 - 4 / 2
```

## calculate 工具说明

- 入参：`expression`（字符串）
- 支持：数字、空格、小数点、括号、`+ - * / // % **`
- 返回：计算结果字符串或错误信息

## 二次开发

接入新工具的最小步骤：

1. 定义一个带类型注解和 docstring 的 Python 函数
2. 将函数加入 `AVAILABLE_TOOLS`
3. 在 `AGENT_SYSTEM_PROMPT` 中补充工具说明
