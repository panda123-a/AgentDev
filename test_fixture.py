import pytest


@pytest.fixture
def sample_data():
    print("准备测试数据")
    data = [1, 2, 3]

    yield data

    print("清理测试数据")


def test_sample_data(sample_data):
    print("开始测试")
    assert sample_data == [1, 2, 3]
    print("测试结束")