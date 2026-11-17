from app import save_history, load_history, DB_FILE
import sqlite3
import json

# 准备一条测试聊天记录
session_id = "sqlite_save_test"
messages = [
    {"role": "user", "content": "我正在学习 SQLite"},
    {"role": "assistant", "content": "我们开始验证保存功能了！"}
]

# 调用刚刚添加的保存函数
save_history(session_id, messages)

# 从数据库读取这条记录
with sqlite3.connect(DB_FILE) as conn:
    row = conn.execute(
        "SELECT session_id, messages FROM chat_histories WHERE session_id = ?",
        (session_id,)
    ).fetchone()

# 把 JSON 字符串还原成 Python 列表
saved_messages = json.loads(row[1])

print("会话 ID：", row[0])
print("保存后的聊天记录：", saved_messages)
print("内容是否一致：", saved_messages == messages)


# 测试读取已经保存的会话
loaded_messages = load_history("sqlite_save_test")

print("读取结果：", loaded_messages)
print("读取是否正确：", loaded_messages == messages)

# 测试读取不存在的会话
empty_messages = load_history("session_does_not_exist")

print("不存在的会话：", empty_messages)

# 测试两个不同会话是否相互隔离
session_id_2 = "sqlite_save_test_2"
messages_2 = [
    {"role": "user", "content": "这是第二个会话"},
    {"role": "assistant", "content": "我是第二个会话的回答"}
]

save_history(session_id_2, messages_2)

# 分别读取两个会话
loaded_1 = load_history("sqlite_save_test")
loaded_2 = load_history(session_id_2)

print("第一个会话是否保持原样：", loaded_1 == messages)
print("第二个会话是否保存正确：", loaded_2 == messages_2)
print("两个会话内容是否不同：", loaded_1 != loaded_2)

# 测试同一个会话再次保存时的行为
new_messages = [
    {"role": "user", "content": "这是更新后的会话内容"}
]

save_history("sqlite_save_test", new_messages)

updated_history = load_history("sqlite_save_test")

print("更新后的聊天记录：", updated_history)
print("是否等于新传入的内容：", updated_history == new_messages)