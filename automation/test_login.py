
def assert_login_rejected(response):
    """拒绝登录应返回客户端错误，且响应不能包含有效令牌。"""
    assert 400 <= response.status_code < 500, (
        f"登录拒绝应返回 4xx，实际状态码为 {response.status_code}"
    )

    data = response.json()
    assert isinstance(data, dict), "登录失败响应应为 JSON 对象"
    assert not data.get("access_token"), "登录失败响应不应包含访问令牌"


def test_login_success(api_client):
    """验证正确的账号密码可以登录。"""
    response = api_client.post(
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


def test_login_with_wrong_password(api_client):
    """验证错误密码不能成功登录。"""
    response = api_client.post(
        "/users/login",
        json={
            "email": "customer@practicesoftwaretesting.com",
            "password": "wrong_password_123",
        },
    )

    assert_login_rejected(response)


def test_login_without_password(api_client):
    """验证缺少密码时不能成功登录。"""
    response = api_client.post(
        "/users/login",
        json={
            "email": "customer@practicesoftwaretesting.com",
        },
    )

    assert_login_rejected(response)
