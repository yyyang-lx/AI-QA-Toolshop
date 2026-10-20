
import requests

BASE_URL = "https://api-with-bugs.practicesoftwaretesting.com"
API_URL = "/products"


def get_response():
    """请求商品列表接口，不读取环境中的代理配置。"""
    session = requests.Session()
    session.trust_env = False
    return session.get(BASE_URL + API_URL, timeout=15)


def test_product_list_api_status_code():
    """验证商品列表接口返回 HTTP 200。"""
    response = get_response()
    assert response.status_code == 200


def test_product_list_api_returns_json():
    """验证接口返回的数据可以解析为 JSON。"""
    response = get_response()
    assert response.status_code == 200
    data = response.json()
    assert data is not None


def test_product_list_contains_products():
    """验证商品列表中存在商品数据。"""
    response = get_response()
    assert response.status_code == 200
    data = response.json()

    products = data if isinstance(data, list) else data.get("data", [])

    assert isinstance(products, list)
    assert len(products) > 0
    for product in products:
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert product["id"] is not None
        assert product["name"].strip() != ""
        assert float(product["price"]) >= 0

def test_search_products_by_keyword():
    """验证使用关键词可以搜索到匹配的商品。"""
    session = requests.Session()
    session.trust_env = False

    response = session.get(
        f"{BASE_URL}/products/search",
        params={"q": "pliers"},
        timeout=15,
    )

    assert response.status_code == 200
    data = response.json()
    products = data if isinstance(data, list) else data.get("data", [])

    assert isinstance(products, list)
    assert len(products) > 0


def test_search_products_with_unmatched_keyword():
    """验证不存在的关键词不会返回匹配商品。"""
    session = requests.Session()
    session.trust_env = False

    response = session.get(
        f"{BASE_URL}/products/search",
        params={"q": "xyznonexistent123"},
        timeout=15,
    )

    assert response.status_code == 200
    data = response.json()
    products = data if isinstance(data, list) else data.get("data", [])

    assert isinstance(products, list)
    assert len(products) == 0
