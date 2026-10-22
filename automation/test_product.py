
from automation.api_client import APIClient


def get_products(response):
    """按分页响应结构提取商品列表。"""
    data = response.json()

    assert isinstance(data, dict), "商品接口响应应为分页 JSON 对象"
    products = data.get("data")
    assert isinstance(products, list), "商品接口响应的 data 字段应为列表"
    return products


def assert_product_shape(product):
    """验证单个商品的关键字段及类型。"""
    assert isinstance(product, dict), "商品项应为 JSON 对象"
    product_id = product.get("id")
    assert isinstance(product_id, int) and not isinstance(product_id, bool), (
        "商品 id 应为整数"
    )
    assert isinstance(product.get("name"), str) and product["name"].strip(), (
        "商品 name 应为非空字符串"
    )
    price = product.get("price")
    assert isinstance(price, (int, float)) and not isinstance(price, bool), (
        "商品 price 应为数字"
    )
    assert price >= 0, "商品 price 不应为负数"


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
            assert_product_shape(product)
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
            assert_product_shape(product)
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
