from types import SimpleNamespace
from unittest.mock import MagicMock
from agent import Agent
import pytest

def test_agent_returns_final_answer():
    client = MagicMock()

    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="你好！",
                    tool_calls=None,
                )
            )
        ]
    )



    agent = Agent(client)

    answer = agent.run("你好")

    assert answer == "你好！"
    assert len(agent.messages) == 2
    assert agent.messages[0]["role"] == "user"
    assert agent.messages[1]["role"] == "assistant"
    client.chat.completions.create.assert_called_once()



def test_agent_calls_calculator():
    client = MagicMock()

    # 第一次响应：模拟大模型要求调用计算器
    tool_call = SimpleNamespace(
        id="call_123",
        function=SimpleNamespace(
            name="calculator",
            arguments='{"expression": "2+3"}',
        ),
    )

    first_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call],
                )
            )
        ]
    )

    # 第二次响应：模拟大模型给出最终回答
    second_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="计算结果是 5",
                    tool_calls=None,
                )
            )
        ]
    )

    # 让大模型接口按顺序返回这两次响应
    client.chat.completions.create.side_effect = [
        first_response,
        second_response,
    ]

    agent = Agent(client)
    answer = agent.run("帮我计算 2+3")

    # 检查最终回答
    assert answer == "计算结果是 5"

    # 检查工具结果是否被保存
    tool_messages = [
        message
        for message in agent.messages
        if message["role"] == "tool"
    ]

    assert len(tool_messages) == 1
    assert tool_messages[0]["content"] == "5"
    assert tool_messages[0]["tool_call_id"] == "call_123"

    # 检查大模型接口是否调用了两次
    assert client.chat.completions.create.call_count == 2

    second_call_messages = (
    client.chat.completions.create.call_args_list[1]
    .kwargs["messages"]
    )

    assert any(
        message.get("role") == "tool"
        and message.get("content") == "5"
        for message in second_call_messages
    )

def test_agent_calls_unknown_tool():
    client = MagicMock()

    tool_call = SimpleNamespace(
        id="call_bad",
        function=SimpleNamespace(
            name="weather_tool",
            arguments="{}",
        ),
    )

    first_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call],
                )
            )
        ]
    )

    client.chat.completions.create.return_value = first_response

    agent = Agent(client)

    answer = agent.run("查询天气")

    assert "weather_tool" in answer
    assert "未知工具" in answer

    
