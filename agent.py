import json
import os
import copy
from openai import OpenAI
from tools import tools, tool_registry

from dotenv import load_dotenv

load_dotenv()


class Agent:
    """通过大模型调用工具并生成最终回答。"""

    def __init__(self, client,model="deepseek-chat"):
        self.client = client
        self.model = model
        self.tools = tools
        self.tool_registry = tool_registry
        self.messages = []

    def run(self, user_input):
        """处理用户输入，必要时循环调用工具。"""

        # 1. 备份本次请求开始前的消息历史
        old_messages = copy.deepcopy(self.messages)

        try:
            # 2. 从这里开始，保留你原有的 Agent 执行逻辑
            self.messages.append({
                "role": "user",
                "content": user_input,
            })

            while True:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tools,
                )

                message = response.choices[0].message

                if not message.tool_calls:
                    self.messages.append({
                        "role": "assistant",
                        "content": message.content,
                    })
                    return message.content

                self.messages.append({
                    "role": "assistant",
                    "tool_calls": message.tool_calls,
                })

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    if tool_name not in self.tool_registry:
                        raise ValueError(f"未知工具：{tool_name}")

                    tool = self.tool_registry[tool_name]
                    result = tool(**arguments)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })

        except Exception:
            # 3. 失败时恢复本次请求开始前的历史
            self.messages = old_messages

            # 4. 继续向上抛出原始异常
            raise


if __name__ == "__main__":
    agent=Agent(
        client= OpenAI(api_key= os.getenv("DEEPSEEK_API_KEY"),
                       base_url="https://api.deepseek.com"
                    ),
        model="deepseek-chat"
    )


    import copy
    from types import SimpleNamespace

    # 1. 暂时准备两条已有聊天记录
    agent.messages = [
        {"role": "user", "content": "Python 是什么？"},
        {"role": "assistant", "content": "Python 是一种编程语言。"}
    ]

    # 2. 备份现有历史
    before_messages = copy.deepcopy(agent.messages)
    original_client = agent.client

    # 3. 模拟 API 调用失败
    def fail_request(**kwargs):
        raise RuntimeError("模拟 API 调用失败")

    agent.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=fail_request
            )
        )
    )

    try:
        agent.run("请继续介绍 Python")
    except RuntimeError as e:
        print("捕获到预期异常：", e)
    finally:
        agent.client = original_client

    # 4. 检查恢复结果
    print("异常前消息数量：", len(before_messages))
    print("异常后消息数量：", len(agent.messages))
    print("消息历史完全恢复：", agent.messages == before_messages)
    print("恢复后的历史：", agent.messages)