import sqlite3
import json
from app import DB_FILE

# 连接已有的数据库
with sqlite3.connect(DB_FILE) as conn:
    # 准备一条模拟聊天记录
    session_id = "demo_session"
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮你？"}
    ]

    # 把 Python 列表转换成 JSON 字符串
    messages_json = json.dumps(messages, ensure_ascii=False)

    # 从 SQLite 读取已有的聊天记录
    row = conn.execute(
        """
        SELECT session_id, messages
        FROM chat_histories
        WHERE session_id = ?
        """,
        ("demo_session",)
    ).fetchone()

    print("查询结果：", row)

messages_json = row[1]
messages = json.loads(messages_json)

print("转换后的聊天记录：", messages)
print("数据类型：", type(messages))
