import pytest

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
        f"商品 id 应为整数，实际值={product_id!r}"
    )

    name = product.get("name")
    assert isinstance(name, str), (
        f"商品 name 应为字符串，实际值={name!r}"
    )
    assert name.strip(), (
        f"商品 name 应为非空字符串，实际值={name!r}"
    )

    price = product.get("price")
    assert isinstance(price, (int, float)) and not isinstance(price, bool), (
        f"商品 price 应为数字，实际值={price!r}"
    )
    assert price >= 0, (
        f"商品 price 不应为负数，实际值={price!r}"
    )


def test_product_shape_valid():
    """验证正常商品可以通过字段校验。"""
    product = {
        "id": 1,
        "name": "Pliers",
        "price": 10,
    }

    assert_product_shape(product)


@pytest.mark.parametrize(
    "product",
    [
        pytest.param(
            {"id": 1, "name": "", "price": 10},
            id="empty-product-name",
        ),
        pytest.param(
            {"id": 1, "name": "Pliers", "price": -5},
            id="negative-product-price",
        ),
        pytest.param(
            {"id": "abc", "name": "Pliers", "price": 10},
            id="invalid-product-id",
        ),
        pytest.param(
            {"id": 1, "name": "Pliers", "price": None},
            id="non-numeric-product-price",
        ),
    ],
)
def test_product_shape_invalid(product):
    """验证异常商品数据会触发断言失败。"""
    with pytest.raises(AssertionError):
        assert_product_shape(product)


def test_product_list_api_status_code(api_client):
    """验证商品列表接口返回 HTTP 200。"""
    response = api_client.get("/products")
    assert response.status_code == 200


def test_product_list_api_returns_json(api_client):
    """验证商品列表接口返回可解析的 JSON。"""

    response = api_client.get("/products")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")
    data = response.json()
    assert isinstance(data, dict), "商品接口响应应为分页 JSON 对象"


def test_product_list_contains_products(api_client):
    """验证商品列表包含结构合理的商品数据。"""
    response = api_client.get("/products")
    assert response.status_code == 200

    products = get_products(response)
    assert len(products) > 0

    for product in products:
        assert_product_shape(product)


def test_search_products_by_keyword(api_client):
    """验证搜索结果中包含匹配关键词的商品。"""
    keyword = "pliers"

    response = api_client.get("/products/search", params={"q": keyword})
    assert response.status_code == 200

    products = get_products(response)

    assert len(products) > 0

    for product in products:
        assert_product_shape(product)
        assert keyword.lower() in product["name"].lower()


def test_search_products_with_unmatched_keyword(api_client):
    """验证不存在的关键词返回空商品列表。"""
    keyword = "xyznonexistent123"

    response = api_client.get(
        "/products/search",
        params={"q": keyword},
    )
    assert response.status_code == 200

    products = get_products(response)
    assert len(products) == 0


def test_search_products_with_empty_keyword(api_client):
    """验证空关键词搜索接口的实际行为。"""
    response = api_client.get(
        "/products/search",
        params={"q": ""},
    )

    assert response.status_code == 200

    products = get_products(response)
    assert len(products) > 0


def test_search_products_without_keyword(api_client):
    """观察缺少 q 参数时搜索接口的实际响应。"""
    response = api_client.get("/products/search")

    print("状态码：", response.status_code)
    print("响应内容：", response.text)


def test_search_products_with_whitespace_keyword(api_client):
    """验证纯空格关键词搜索返回空商品列表。"""
    response = api_client.get(
        "/products/search",
        params={"q": "   "},
    )

    assert response.status_code == 200

    products = get_products(response)
    assert len(products) == 0


def test_search_products_by_uppercase_keyword(api_client):
    """验证大写关键词能否匹配商品名称。"""
    keyword = "PLIERS"

    response = api_client.get(
        "/products/search",
        params={"q": keyword},
    )

    assert response.status_code == 200

    products = get_products(response)
    assert len(products) > 0

    for product in products:
        assert_product_shape(product)
        assert keyword.lower() in product["name"].lower()

def test_search_products_by_mixed_case_keyword(api_client):
    """验证混合大小写关键词能否匹配商品名称。"""
    keyword = "PliERS"

    response = api_client.get(
        "/products/search",
        params={"q": keyword},
    )

    lower_response = api_client.get(
        "/products/search",
        params={"q": keyword.lower()},
    )
    assert response.status_code == 200
    assert lower_response.status_code == 200

    products = get_products(response)
    for product in products:
        assert_product_shape(product)
        assert keyword.lower() in product["name"].lower()
    lower_products = get_products(lower_response)

    lower_ids = [product["id"] for product in lower_products]
    mixed_ids = [product["id"] for product in products]
    assert set(lower_ids) == set(mixed_ids)
