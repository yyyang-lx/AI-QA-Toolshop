
from automation.api_client import APIClient


def test_login_success():
    """验证正确的账号密码可以登录。"""
    client = APIClient()

    try:
        response = client.post(
            "/users/login",
            json={
                "email": "customer@practicesoftwaretesting.com",
                "password": "welcome01",
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert data.get("access_token")
        assert data.get("token_type", "").lower() == "bearer"
        assert data.get("expires_in", 0) > 0
    finally:
        client.close()


def test_login_with_wrong_password():
    """验证错误密码不能成功登录。"""
    client = APIClient()

    try:
        response = client.post(
            "/users/login",
            json={
                "email": "customer@practicesoftwaretesting.com",
                "password": "wrong_password_123",
            },
        )

        assert response.status_code != 200

        data = response.json()
        assert not data.get("access_token")
    finally:
        client.close()


def test_login_without_password():
    """验证缺少密码时不能成功登录。"""
    client = APIClient()

    try:
        response = client.post(
            "/users/login",
            json={
                "email": "customer@practicesoftwaretesting.com",
            },
        )

        assert response.status_code != 200

        data = response.json()
        assert not data.get("access_token")
    finally:
        client.close()
