# AI Agent 智能问答系统

基于 Python、DeepSeek 大语言模型和 FastAPI 构建的 AI Agent 智能问答系统，支持工具调用、RAG 知识检索、多轮对话、会话隔离及聊天历史持久化。

## 项目简介

本项目通过 Agent Loop 实现大语言模型与工具之间的交互，支持模型根据用户问题决定是否调用工具；通过 RAG 检索本地知识库，为模型回答提供相关资料；通过 FastAPI 提供 HTTP 接口，并使用 `session_id` 区分不同会话。

系统将聊天历史保存到 JSON 文件中，支持应用重启后的历史恢复，并通过临时文件替换方式保存历史数据，降低写入过程中损坏原文件的风险。

## 核心功能

- **Agent 工具调用**：支持模型根据问题决定是否调用工具，并处理工具执行结果。
- **RAG 知识检索**：基于中文文本嵌入和相似度检索，从本地知识库中查找相关资料。
- **多轮对话**：维护消息历史，为后续回答提供上下文。
- **会话隔离**：通过 `session_id` 区分不同会话。
- **历史持久化**：将聊天历史保存到 JSON 文件，并在后续请求中恢复。
- **REST API**：使用 FastAPI 提供聊天接口，支持通过 Swagger UI 调试。
- **异常处理与日志记录**：记录请求处理异常，并通过临时文件替换方式保存聊天历史。

## 技术栈

| 技术 | 用途 |
|---|---|
| Python | 核心开发语言 |
| DeepSeek API | 大语言模型调用 |
| Agent Loop | 管理模型与工具之间的交互 |
| RAG | 检索本地知识库 |
| Sentence Transformers / BGE | 中文文本向量化 |
| FastAPI | 提供 HTTP API |
| Pydantic | 请求参数校验 |
| JSON | 保存聊天历史 |
| Git / GitHub | 版本管理与代码托管 |

## 项目结构

```text
AgentDev/
├── app.py                # FastAPI 接口、会话管理、历史持久化
├── agent.py              # Agent 主循环、模型交互、工具调用
├── tools.py              # 工具定义与工具注册
├── rag.py                # RAG 知识检索与问答
├── knowledge_base.pkl    # 本地知识库数据
├── requirements.txt      # Python 依赖清单
├── test_agent.py         # Agent 相关测试代码
├── test_rag.py           # RAG 相关测试代码
├── test_agent.ipynb      # 实验与调试笔记本
├── README.md             # 项目说明文档
├── .env                  # 本地环境变量，不应提交
└── chat_history.json     # 运行时生成的聊天历史，不应提交
```

> `.env` 和 `chat_history.json` 是本地运行时文件，已通过 `.gitignore` 排除在版本管理之外。上面的目录树用于说明项目组成，不代表所有文件都会出现在 GitHub 仓库中。

## 核心模块职责

| 模块 | 职责 |
|---|---|
| `app.py` | 接收 HTTP 请求、管理会话、加载和保存聊天历史 |
| `agent.py` | 调用大语言模型、维护消息历史、执行 Agent Loop |
| `tools.py` | 定义可供 Agent 调用的工具，并维护工具注册关系 |
| `rag.py` | 检索本地知识库，为问答提供相关上下文 |
| `knowledge_base.pkl` | 保存已构建的知识库数据 |
| `requirements.txt` | 记录项目所需的 Python 依赖 |

## 系统处理流程

```text
用户提交问题
    │
    ▼
FastAPI 接收请求
    │
    ▼
根据 session_id 获取或创建 Agent
    │
    ▼
恢复已有会话历史（如有）
    │
    ▼
Agent 将问题与上下文发送给 DeepSeek
    │
    ▼
模型是否需要调用工具？
    │
    ├── 是 ──► 执行工具 ──► 将工具结果加入消息历史
    │                         │
    │                         └──► 继续模型交互
    │
    └── 否 ──► 获取最终回答
                    │
                    ▼
          序列化并保存会话历史
                    │
                    ▼
          返回回答和 session_id
```

> 以上流程为逻辑示意，具体行为以当前代码实现为准。

## 环境要求

- Python 3.12
- 可用的 DeepSeek API Key
- Windows、Linux 或 macOS

以下安装与启动命令以 Windows PowerShell 为例。

## 安装与配置

### 1. 获取项目代码

```powershell
git clone https://github.com/panda123-a/AgentDev.git
cd AgentDev
```

### 2. 创建虚拟环境

```powershell
python -m venv agent_env
```

激活虚拟环境：

```powershell
.\agent_env\Scripts\Activate.ps1
```

如果你已经创建过项目虚拟环境，可以直接激活现有环境。

### 3. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

如果不想激活虚拟环境，也可以直接使用虚拟环境中的 Python：

```powershell
.\agent_env\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. 配置 API Key

在项目根目录创建 `.env` 文件，添加以下内容：

```dotenv
DEEPSEEK_API_KEY=替换为你自己的DeepSeek_API_Key
```

将示例值替换为自己的有效 API Key。

**安全提示：**

- 不要将真实 API Key 写入源代码或 README。
- 不要将 `.env` 文件提交到公开仓库。
- 不要在截图、日志或示例输出中暴露真实密钥。

### 5. 启动服务

在项目根目录执行：

```powershell
python app.py
```

如果没有激活虚拟环境，可以执行：

```powershell
.\agent_env\Scripts\python.exe app.py
```

服务启动后，默认访问地址如下：

| 地址 | 用途 |
|---|---|
| `http://127.0.0.1:8000` | 服务入口 |
| `http://127.0.0.1:8000/docs` | Swagger API 文档 |

## API 使用说明

### `GET /`

检查服务是否启动。

### `POST /chat`

向 Agent 发送问题，获取模型生成的回答。

**请求示例：**

```json
{
  "question": "请介绍一下知识库中的 Agent 工具调用机制",
  "session_id": "demo-session"
}
```

`session_id` 为可选参数。首次请求可以不传，系统会自动生成会话 ID。

**响应示例：**

```json
{
  "answer": "Agent 会根据用户问题判断是否需要调用工具，并结合工具执行结果生成回答。",
  "session_id": "demo-session"
}
```

以上回答仅为格式示例，实际回答取决于模型、问题和知识库内容。

### 参数说明

| 参数 | 是否必填 | 说明 |
|---|---|---|
| `question` | 是 | 用户问题，长度为 1～2000 个字符 |
| `session_id` | 否 | 会话标识；相同 ID 用于继续对应会话 |

## 会话历史持久化

系统将会话消息序列化后保存到 `chat_history.json` 文件中。

- 使用相同的 `session_id` 可以继续已有会话。
- 服务重启后，可以从已保存的历史记录恢复会话。
- 保存时先写入临时文件，再使用文件替换操作更新正式历史文件，以降低写入中断导致原文件损坏的风险。

注意：当前文件式存储适合学习和演示。若要用于多进程部署、多人并发或生产环境，建议进一步改用 SQLite、PostgreSQL 等数据库，并补充相应的数据隔离与并发控制。

## 在线调试

启动服务后，打开：

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

在 Swagger UI 中找到 `POST /chat`，点击 **Try it out**，填写请求参数并执行，即可查看接口响应。

## 项目说明

本项目用于学习和实践 AI Agent 应用开发，涵盖模型调用、工具调用、RAG 检索、FastAPI 接口、会话管理和本地历史持久化等内容。

欢迎交流与反馈。