import copy
import pytest
from unittest.mock import patch
import app


@pytest.fixture
def test_agent():
    session_id = "save_failure_test"

    agent = app.Agent(client=app.client, model="deepseek-chat")

    agent.messages = [
        {"role": "user", "content": "之前的问题"},
        {"role": "assistant", "content": "之前的回答"},
    ]

    app.agents[session_id] = agent

    # 把测试需要的对象交给测试函数
    yield session_id, agent

    # 测试结束后自动清理
    app.agents.pop(session_id, None)


def test_chat_rolls_back_when_save_fails(test_agent):
    session_id, agent = test_agent

    old_messages = copy.deepcopy(agent.messages)

    def fake_run(question):
        agent.messages.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": "新的回答"},
        ])
        return "新的回答"

    with (
        patch("app.load_history", return_value=copy.deepcopy(old_messages)),
        patch.object(agent, "run", side_effect=fake_run),
        patch("app.save_history", side_effect=RuntimeError("模拟数据库保存失败")),
    ):
        with pytest.raises(app.HTTPException) as exc_info:
            app.chat(
                app.ChatRequest(
                    question="新的问题",
                    session_id=session_id
                )
            )

    # 验证接口返回 HTTP 500
    assert exc_info.value.status_code == 500

    # 验证 Agent 历史记录恢复
    assert agent.messages == old_messages
    assert len(agent.messages) == 2