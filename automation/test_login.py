
import requests

BASE_URL = "https://api-with-bugs.practicesoftwaretesting.com"


def test_login_success():
    """验证正确的登录凭据能够获取访问令牌。"""
    session = requests.Session()
    session.trust_env = False

    response = session.post(
        f"{BASE_URL}/users/login",
        json={
            "email": "customer@practicesoftwaretesting.com",
            "password": "welcome01",
        },
        timeout=15,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["token_type"].lower() == "bearer"
    assert data["expires_in"] > 0

def test_login_with_wrong_password():
    """验证错误密码不能登录成功。"""
    session = requests.Session()
    session.trust_env = False

    response = session.post(
        f"{BASE_URL}/users/login",
        json={
            "email": "customer@practicesoftwaretesting.com",
            "password": "WrongPassword123!",
        },
        timeout=15,
    )

    assert response.status_code != 200

    data = response.json()
    assert not data.get("access_token")


def test_login_without_password():
    """验证缺少密码时，登录请求不能成功。"""
    session = requests.Session()
    session.trust_env = False

    response = session.post(
        f"{BASE_URL}/users/login",
        json={
            "email": "customer@practicesoftwaretesting.com",
        },
        timeout=15,
    )

    assert response.status_code != 200

    data = response.json()
    assert not data.get("access_token")
