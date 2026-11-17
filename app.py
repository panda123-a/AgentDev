import os
import copy
import json
import sqlite3

from pathlib import Path
from contextlib import closing
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
import logging
from logging.handlers import RotatingFileHandler

from agent import Agent
from config import API_KEY, MODEL_NAME, BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DB_FILE = Path(__file__).with_name("chat_history.db")


def init_db():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_histories (
                    session_id TEXT PRIMARY KEY,
                    messages TEXT NOT NULL
                )
            """)


init_db()


def save_history(session_id, messages):
    messages_json = json.dumps(messages, ensure_ascii=False)

    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO chat_histories (session_id, messages)
                VALUES (?, ?)
                ON CONFLICT(session_id)
                DO UPDATE SET messages = excluded.messages
                """,
                (session_id, messages_json),
            )


def load_history(session_id):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            row = conn.execute(
                """
                    SELECT session_id, messages
                    FROM chat_histories 
                    WHERE session_id=?
                    """,
                (session_id,),
            ).fetchone()
    if not row:
        messages = []

    else:
        messages = json.loads(row[1])
    return messages


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
    api_key=API_KEY,
    base_url=BASE_URL,
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


@app.get("/")
def home():
    return {"message": "Agent API 已启动"}


agents = {}


@app.post("/chat")
def chat(request: ChatRequest):
    try:

        session_id = request.session_id

        if not session_id:
            session_id = str(uuid4())

        logger.info("收到聊天请求，session_id=%s", session_id)

        history = load_history(session_id)

        if session_id not in agents:
            agent = Agent(client=client, model=MODEL_NAME)

            # 恢复这个会话之前保存的消息
            agent.messages = copy.deepcopy(history)

            # 将新创建的 Agent 存入字典
            agents[session_id] = agent

        agent = agents[session_id]

        # 备份本轮执行前的消息历史
        old_messages = copy.deepcopy(agent.messages)

        # 执行当前用户的问题
        answer = agent.run(request.question)

        logger.info("Agent 执行成功，session_id=%s", session_id)

        # 保存当前会话的完整历史
        history = serialize_messages(agent.messages)

        try:
            save_history(session_id, history)
            logger.info("聊天历史保存成功，session_id=%s", session_id)
        except Exception:
            agent.messages = old_messages
            raise

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
