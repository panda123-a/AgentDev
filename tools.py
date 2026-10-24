
import os
from dotenv import load_dotenv

from rag import load_rag_resources, rag_query


# 确保读取项目目录下的 .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# 加载一次 RAG 资源，供知识库工具重复使用
documents = None
embeddings = None
model = None
client = None


def calculator(expression: str):
    """计算数学表达式并返回结果。"""
    return eval(expression)


def get_number() -> int:
    """返回数字 100。"""
    return 100


def search_knowledge_base(query: str) -> str:
    global documents, embeddings, model, client

    # 只有第一次调用时才加载
    if model is None:
        documents, embeddings, model, client = load_rag_resources()

    return rag_query(
        query=query,
        documents=documents,
        embeddings=embeddings,
        model=model,
        client=client,
    )


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "需要计算的数学表达式，例如 123 * 456",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_number",
            "description": "返回数字 100",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "查询本地知识库，回答有关 Python、AI Agent、RAG 等知识库内容的问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要查询知识库的问题",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

# 将模型返回的工具名称映射到实际的 Python 函数。
tool_registry = {
    "calculator": calculator,
    "get_number": get_number,
    "search_knowledge_base": search_knowledge_base,
}