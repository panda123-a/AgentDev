from rag import retrieve_documents



class FakeModel:
    """模拟向量模型，避免加载真实模型或调用外部服务。"""

    def encode(self, text):
        if text == "问题":
            return [1.0, 0.0]
        return text


def test_retrieve_documents_returns_top_match():
    documents = ["相关资料", "无关资料"]
    embeddings = [
        [0.9, 0.1],
        [0.0, 1.0],
    ]

    results = retrieve_documents(
        query="问题",
        documents=documents,
        embeddings=embeddings,
        model=FakeModel(),
        top_k=1,
        similarity_threshold=0.6,
    )

    assert len(results) == 1
    assert results[0][1] == "相关资料"
    assert results[0][0] > 0.6


def test_retrieve_documents_returns_empty_when_no_match():
    documents = ["无关资料"]
    embeddings = [[0.0, 1.0]]

    results = retrieve_documents(
        query="问题",
        documents=documents,
        embeddings=embeddings,
        model=FakeModel(),
        similarity_threshold=0.6,
    )

    assert results == []