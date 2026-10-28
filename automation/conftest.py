import pytest
from automation.api_client import APIClient
"""封装客户端"""
@pytest.fixture
def api_client():
    client = APIClient()
    try:
        yield client
    finally:
        client.close()
