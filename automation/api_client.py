
from automation.config import BASE_URL, REQUEST_TIMEOUT, create_session


class APIClient:
    """封装通用 HTTP 请求，供 API 自动化测试复用。"""

    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = REQUEST_TIMEOUT
        self.session = create_session()

    def get(self, path, **kwargs):
        """发送 GET 请求。"""
        return self.session.get(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )

    def post(self, path, **kwargs):
        """发送 POST 请求。"""
        return self.session.post(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )

    def close(self):
        """关闭 HTTP 会话，释放连接资源。"""
        self.session.close()
