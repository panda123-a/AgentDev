AI Agent 智能问答系统

项目简介

本项目基于 Python、DeepSeek 大语言模型和 FastAPI，开发了一个支持工具调用、RAG 知识检索、多轮对话和会话历史持久化的 AI Agent 智能问答系统。

系统通过 Agent Loop 实现模型与工具之间的交互，支持根据用户问题调用工具；通过 RAG 检索本地知识库，为模型提供相关资料；通过 FastAPI 提供 HTTP 接口，并使用会话 ID 区分不同会话，将聊天历史保存到 JSON 文件中，支持应用重启后的历史恢复。

核心功能

Agent 工具调用：支持模型根据问题决定是否调用工具，并处理工具返回结果。

RAG 知识检索：基于中文文本嵌入和相似度检索，从本地知识库中查找相关资料。

多轮对话：维护会话消息历史，为后续回答提供上下文。

会话隔离：通过 session_id 区分不同会话。

历史持久化：将聊天历史保存到 JSON 文件，并在后续请求中恢复。

REST API：使用 FastAPI 提供聊天接口，并支持通过 Swagger UI 调试接口。

异常处理与安全保存：使用日志记录异常，并通过临时文件替换方式保存聊天历史。



项目架构

目录结构

D:\AgentDev
├── app.py              # FastAPI 接口、会话管理、历史持久化
├── agent.py            # Agent 主循环、模型交互、工具调用
├── tools.py            # 工具定义与工具注册
├── rag.py              # RAG 知识检索与问答
├── knowledge_base.pkl  # 本地知识库数据
├── chat_history.json   # 聊天历史数据（运行时生成）
├── requirements.txt    # 项目依赖清单
├── test_agent.py       # Agent 相关测试代码
├── test_rag.py         # RAG 相关测试代码
├── test_agent.ipynb    # 实验与调试笔记本
├── README.md           # 项目说明文档
└── .env                # 环境变量配置，不应提交到公开仓库

核心模块职责

模块

职责

app.py

接收 HTTP 请求、管理会话、加载和保存聊天历史

agent.py

调用大语言模型、维护消息历史、执行 Agent Loop

tools.py

定义可供 Agent 调用的工具，并维护工具注册关系

rag.py

检索本地知识库，为问答提供相关上下文

knowledge_base.pkl

保存已经构建的知识库数据

chat_history.json

持久化各会话的消息历史

请求处理流程

用户通过 FastAPI 的 /chat 接口提交问题。

系统根据 session_id 查找现有 Agent；如果是已有历史会话，则恢复对应的消息历史。

Agent 将当前问题和消息上下文发送给 DeepSeek 模型。

如果模型要求调用工具，Agent 执行相应工具，并将工具结果加入消息历史。

Agent 根据模型返回结果继续处理，直到得到最终回答。

系统序列化当前会话历史，并通过临时文件替换方式保存到 JSON 文件。

API 返回回答内容和 session_id。

说明：上述流程应以当前代码的实际执行逻辑为准。若某一步与最新代码不一致，应先核对实现再修改文档。



## 环境要求

- Python 3.12
- DeepSeek API Key
- Windows、Linux 或 macOS（以下命令以 Windows PowerShell 为例）

## 安装与配置

### 1. 创建并激活虚拟环境

在项目根目录打开终端，执行：

```powershell
python -m venv agent_env
.\agent_env\Scripts\Activate.ps1
```

如果本机已有项目虚拟环境，可以直接激活现有环境。

### 2. 安装依赖

在项目根目录执行：

```powershell
.\agent_env\Scripts\python.exe -m pip install -r requirements.txt
```

该命令会根据 `requirements.txt` 安装项目所需的 Python 依赖。

### 3. 配置环境变量

在项目根目录创建 `.env` 文件，添加：

```dotenv
DEEPSEEK_API_KEY=替换为你自己的DeepSeek_API_Key
```

请填写自己的有效 API Key，不要将真实密钥写进 README，也不要提交 `.env` 到公开代码仓库。

### 4. 启动服务

在项目根目录运行：

```powershell
.\agent_env\Scripts\python.exe app.py
```

服务启动后，默认访问地址为：

- API 地址：`http://127.0.0.1:8000`
- Swagger 接口文档：`http://127.0.0.1:8000/docs`

## 接口使用

### `GET /`

检查服务是否启动。

### `POST /chat`

接口地址： POST /chat

向 Agent 发送问题，获取 AI 生成的回答。

请求示例

{
  "question": "请介绍一下知识库中的 Agent 工具调用机制",
  "session_id": "demo-session"
}

响应示例

{
  "answer": "Agent 会根据用户问题判断是否需要调用工具，并结合工具执行结果生成回答。",
  "session_id": "demo-session"
}

会话管理

question：必填，长度为 1～2000 个字符。

session_id：选填。首次请求可不传，服务会自动生成会话 ID。

使用相同的 session_id 可以继续之前的对话。

会话历史保存在 chat_history.json，服务重启后可恢复已保存的历史消息。

在线调试

启动服务后，访问 Swagger API 文档，即可在线发送请求并查看响应。