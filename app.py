import os
import copy
import json
from pathlib import Path

from uuid import uuid4
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
import logging

from agent import Agent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HISTORY_FILE = Path(__file__).with_name("chat_history.json")
temp_path = HISTORY_FILE.with_suffix(".tmp")


def load_histories():
    if not HISTORY_FILE.exists():
        return {}

    with HISTORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_histories(histories):
    try:
         # 在这里完成临时文件写入
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(histories, f, ensure_ascii=False, indent=2)
        
        # 文件成功关闭后，替换正式文件
        os.replace(temp_path,HISTORY_FILE)
        
    except Exception :
        # 记录错误日志
        logger.exception("聊天历史保存失败")
        #  重新抛出异常
        raise


def serialize_messages(messages):
    """将 Agent 历史转换为可保存到 JSON 的数据。"""
    serialized = []

    for message in messages:
        new_message = message.copy()

        if "tool_calls" in new_message:
            new_message["tool_calls"] = [
                (
                    tool_call.model_dump(mode="json")
                    if hasattr(tool_call, "model_dump")
                    else tool_call
                )
                for tool_call in new_message["tool_calls"]
            ]

        serialized.append(new_message)

    return serialized

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

histories = load_histories()
agents = {}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


@app.get("/")
def home():
    return {"message": "Agent API 已启动"}



@app.post("/chat")
def chat(request: ChatRequest):
    try:
        session_id = request.session_id

        if not session_id:
            session_id = str(uuid4())

        if session_id not in agents:
            agent = Agent(client=client,model="deepseek-chat")

            # 恢复这个会话之前保存的消息
            if session_id in histories:
                agent.messages = copy.deepcopy(histories[session_id])

            agents[session_id] = agent

        agent = agents[session_id]

        # 执行当前用户的问题
        answer = agent.run(request.question)

        # 保存当前会话的完整历史
        histories[session_id] = serialize_messages(agent.messages)
        save_histories(histories)

        return {
            "answer": answer,
            "session_id": session_id,
        }

    except Exception:
        logger.exception("Agent 处理请求失败")
        raise HTTPException(
            status_code=500,
            detail="Agent 处理请求失败，请稍后重试",
        )



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
    
