
import requests

# Toolshop API 基础地址
BASE_URL = "https://api-with-bugs.practicesoftwaretesting.com"

# 请求超时时间，单位：秒
REQUEST_TIMEOUT = 15


def create_session():
    """创建统一配置的 HTTP 会话。"""
    session = requests.Session()

    # 读取环境中的代理配置，允许测试请求使用已配置的代理
    session.trust_env = True

    return session
