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
    """[自动化补充·单元级] 验证正常商品可以通过本地字段校验。"""
    product = {
        "id": 1,
        "name": "Pliers",
        "price": 10,
    }

    assert_product_shape(product)



@pytest.mark.parametrize(
    "product, expected_message",
    [
        pytest.param(
            {"id": 1, "name": "", "price": 10},
            "商品 name 应为非空字符串",
            id="empty-product-name",# id为pytest的参数化测试的唯一标识符
        ),
        pytest.param(
            {"id": 1, "name": "Pliers", "price": -5},
            "商品 price 不应为负数",
            id="negative-product-price",
        ),
        pytest.param(
            {"id": "abc", "name": "Pliers", "price": 10},
            "商品 id 应为整数",
            id="invalid-product-id",
        ),
        pytest.param(
            {"id": 1, "name": "Pliers", "price": None},
            "商品 price 应为数字",
            id="non-numeric-product-price",
        ),
    ],
)
def test_product_shape_invalid(product, expected_message):
    """[自动化补充·单元级] 验证异常商品数据触发对应的字段校验错误。"""
    with pytest.raises(AssertionError, match=expected_message):# match正则表达式匹配捕获的异常信息
        assert_product_shape(product)


def test_product_list_api_returns_json(api_client):
    """[自动化补充·API] 验证商品列表接口返回成功状态和正确的 JSON 结构。"""
    response = api_client.get("/products")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")

    data = response.json()
    assert isinstance(data, dict), "商品接口响应应为分页 JSON 对象"
    assert "data" in data
    assert isinstance(data["data"], list)


def test_product_list_contains_products(api_client):
    """[自动化补充·API] 验证商品列表非空且商品字段结构合理。"""
    response = api_client.get("/products")
    assert response.status_code == 200

    products = get_products(response)
    assert len(products) > 0

    for product in products:
        assert_product_shape(product)


def test_product_detail_matches_search_result(api_client):
    """[自动化补充·API，关联 TC006/TC007/TC008] 校验详情接口与搜索结果一致。"""
    search_response = api_client.get(
        "/products/search",
        params={"q": "pliers"},
    )
    assert search_response.status_code == 200

    search_products = get_products(search_response)
    assert search_products, "前置搜索应返回至少一个商品"
    listed_product = search_products[0]

    detail_response = api_client.get(f"/products/{listed_product['id']}")
    assert detail_response.status_code == 200
    assert "application/json" in detail_response.headers.get("Content-Type", "")

    detail_product = detail_response.json()
    assert_product_shape(detail_product)
    assert detail_product["id"] == listed_product["id"]
    assert detail_product["name"] == listed_product["name"], (
        "详情接口中的商品名称应与搜索结果一致"
    )
    assert detail_product["price"] == listed_product["price"], (
        "详情接口中的商品价格应与搜索结果一致"
    )


def test_search_products_by_keyword(api_client):
    """[TC001] 验证可匹配关键词搜索返回名称匹配的商品。"""
    keyword = "pliers"

    response = api_client.get("/products/search", params={"q": keyword})
    assert response.status_code == 200

    products = get_products(response)

    assert len(products) > 0

    for product in products:
        assert_product_shape(product)
        assert keyword.lower() in product["name"].lower()


def test_search_products_with_unmatched_keyword(api_client):
    """[TC002] 验证不存在的关键词返回空商品列表。"""
    keyword = "xyznonexistent123"

    response = api_client.get(
        "/products/search",
        params={"q": keyword},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["data"] == []
    assert body["total"] == 0


def test_search_products_with_spaces_keyword(api_client):
    """[TC004] 验证关键词首尾空格不改变搜索结果。"""
    keyword = "pliers"

    spaced_response = api_client.get(
        "/products/search",
        params={"q": f" {keyword} "},
    )
    standard_response = api_client.get(
        "/products/search",
        params={"q": keyword},
    )
    assert spaced_response.status_code == 200
    assert standard_response.status_code == 200

    spaced_products = get_products(spaced_response)
    standard_products = get_products(standard_response)
    assert spaced_products, "首尾带空格的有效关键词应返回匹配商品"
    assert standard_products, "标准关键词应返回匹配商品"

    for product in spaced_products:
        assert_product_shape(product)
        assert keyword in product["name"].lower()
    for product in standard_products:
        assert_product_shape(product)
        assert keyword in product["name"].lower()

    spaced_ids = {product["id"] for product in spaced_products}
    standard_ids = {product["id"] for product in standard_products}
    assert spaced_ids == standard_ids, "首尾空格不应改变匹配商品集合"


def test_search_products_with_different_keyword(api_client):
    """[TC005] 验证连续更换关键词后，搜索结果随新关键词更新。"""
    first_keyword = "pliers"
    second_keyword = "hammer"

    first_response = api_client.get(
        "/products/search",
        params={"q": first_keyword},
    )
    assert first_response.status_code == 200
    first_products = get_products(first_response)
    assert first_products, f"首次搜索 {first_keyword!r} 应返回商品"

    second_response = api_client.get(
        "/products/search",
        params={"q": second_keyword},
    )
    assert second_response.status_code == 200
    second_products = get_products(second_response)
    assert second_products, f"更换为 {second_keyword!r} 后应返回商品"

    for product in first_products:
        assert_product_shape(product)
        assert first_keyword in product["name"].lower()
    for product in second_products:
        assert_product_shape(product)
        assert second_keyword in product["name"].lower()

    first_ids = {product["id"] for product in first_products}
    second_ids = {product["id"] for product in second_products}
    assert first_ids != second_ids, "更换搜索关键词后，结果商品集合应发生变化"


def test_search_products_with_empty_keyword(api_client):
    """[TC003] 记录并验证空关键词搜索接口当前返回商品的行为。"""
    response = api_client.get(
        "/products/search",
        params={"q": ""},
    )

    assert response.status_code == 200

    products = get_products(response)
    assert len(products) > 0


def test_search_products_with_whitespace_keyword(api_client):
    """[自动化补充·API] 验证纯空格关键词搜索返回空商品列表。"""
    response = api_client.get(
        "/products/search",
        params={"q": "   "},
    )

    assert response.status_code == 200

    products = get_products(response)
    assert len(products) == 0


def test_search_products_by_uppercase_keyword(api_client):
    """[自动化补充·API] 验证大写关键词搜索是否匹配商品名称。"""
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
    """[自动化补充·API] 验证混合大小写关键词搜索是否匹配商品名称。"""
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
    assert len(products) > 0, "混合大小写搜索应返回匹配商品"
    for product in products:
        assert_product_shape(product)
        assert keyword.lower() in product["name"].lower()
    lower_products = get_products(lower_response)

    lower_ids = [product["id"] for product in lower_products]
    mixed_ids = [product["id"] for product in products]
    assert set(lower_ids) == set(mixed_ids)
