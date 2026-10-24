import os
import pickle
import math

from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 读取项目目录中的 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def cosine_similarity(a, b):
    """计算两个向量的余弦相似度，返回浮点数。"""

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x**2 for x in a))
    norm_b = math.sqrt(sum(x**2 for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def load_rag_resources():
    """加载 BGE 模型、DeepSeek 客户端和本地知识库。"""

    model = SentenceTransformer(
        "BAAI/bge-small-zh-v1.5",
        local_files_only=True,
    )

    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    knowledge_base_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "knowledge_base.pkl",
    )

    if os.path.exists(knowledge_base_path):
        with open(knowledge_base_path, "rb") as f:
            knowledge_base = pickle.load(f)

        documents = knowledge_base["documents"]
        embeddings = knowledge_base["embeddings"]

        print("已加载本地知识库，不需要重新向量化。")

    else:
        documents = [
            "Python 是一种编程语言。",
            "Python 可以用于数据分析。",
            "Python 可以用于开发 AI Agent。",
            "Agent 可以通过调用工具完成任务。",
            "RAG 可以检索知识库中的资料。",
        ]

        embeddings = model.encode(documents)

        knowledge_base = {
            "documents": documents,
            "embeddings": embeddings,
        }

        with open(knowledge_base_path, "wb") as f:
            pickle.dump(knowledge_base, f)

        print("知识库已构建并保存。")

    return documents, embeddings, model, client


def retrieve_documents(
    query,
    documents,
    embeddings,
    model,
    top_k=3,
    similarity_threshold=0.6,
):
    """根据相似度检索相关文档，返回 (相似度, 文档内容) 列表。"""

    embedding_q = model.encode(query)
    results = []

    for i, embedding in enumerate(embeddings):
        score = cosine_similarity(embedding_q, embedding)
        results.append((score, documents[i]))

    results.sort(key=lambda x: x[0], reverse=True)

    filtered_results = [
        item
        for item in results
        if item[0] >= similarity_threshold
    ]

    return filtered_results[:top_k]


def generate_answer(query, results, client):
    """根据检索结果调用 DeepSeek 生成回答。"""

    if not results:
        return "知识库中没有找到足够相关的资料"

    context = "\n".join(document for score, document in results)

    prompt = f"""
你是一个严谨的知识库问答助手，请遵守以下规则：
1. 只能根据参考文档中的信息回答问题。
2. 如果参考文档没有提供足够的信息，请明确回答：
   "根据当前知识库，无法找到足够的信息来回答这个问题。"
3. 不要使用已有知识补充参考文档中没有的信息。
4. 不要编造事实。

问题：
{query}

参考文档：
{context}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content


def rag_query(
    query,
    documents,
    embeddings,
    model,
    client,
    top_k=3,
    similarity_threshold=0.6,
):
    """完成检索、过滤和大模型回答的完整流程。"""

    results = retrieve_documents(
        query=query,
        documents=documents,
        embeddings=embeddings,
        model=model,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )

    return generate_answer(
        query=query,
        results=results,
        client=client,
    )



