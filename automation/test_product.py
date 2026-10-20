
from automation.api_client import APIClient


def get_products(response):
    """从接口响应中提取商品列表。"""
    data = response.json()

    if isinstance(data, list):
        return data

    return data.get("data", [])


def test_product_list_api_status_code():
    """验证商品列表接口返回 HTTP 200。"""
    client = APIClient()

    try:
        response = client.get("/products")
        assert response.status_code == 200
    finally:
        client.close()


def test_product_list_api_returns_json():
    """验证商品列表接口返回可解析的 JSON。"""
    client = APIClient()

    try:
        response = client.get("/products")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        response.json()
    finally:
        client.close()


def test_product_list_contains_products():
    """验证商品列表包含结构合理的商品数据。"""
    client = APIClient()

    try:
        response = client.get("/products")
        assert response.status_code == 200

        products = get_products(response)

        assert isinstance(products, list)
        assert len(products) > 0

        for product in products:
            assert product.get("id") is not None
            assert isinstance(product.get("name"), str)
            assert product["name"].strip() != ""
            assert product.get("price") is not None
            assert float(product["price"]) >= 0
    finally:
        client.close()


def test_search_products_by_keyword():
    """验证搜索结果中包含匹配关键词的商品。"""
    keyword = "pliers"
    client = APIClient()

    try:
        response = client.get("/products/search", params={"q": keyword})
        assert response.status_code == 200

        products = get_products(response)

        assert isinstance(products, list)
        assert len(products) > 0

        for product in products:
            assert keyword.lower() in product["name"].lower()
    finally:
        client.close()


def test_search_products_with_unmatched_keyword():
    """验证不存在的关键词返回空商品列表。"""
    keyword = "xyznonexistent123"
    client = APIClient()

    try:
        response = client.get(
            "/products/search",
            params={"q": keyword},
        )
        assert response.status_code == 200

        products = get_products(response)

        assert isinstance(products, list)
        assert len(products) == 0
    finally:
        client.close()
