"""With Bugs 网站首页和购物车 UI 自动化测试。"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import warnings

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect, sync_playwright


BASE_URL = os.getenv(
    "TOOLSHOP_UI_BASE_URL",
    "https://with-bugs.practicesoftwaretesting.com/",
).rstrip("/") + "/"
PRODUCT_NAME = "Combination Pliers"


def save_failure_screenshot(page):
    """将失败页面保存到缺陷截图目录，文件名包含执行时间。"""
    screenshot_dir = Path(__file__).parents[1] / "bugs" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    page.screenshot(path=screenshot_dir / f"cart-ui-{timestamp}.png", full_page=True)


@pytest.fixture
def page():
    """每个测试使用独立浏览器页面。"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        test_page = browser.new_page()
        try:
            yield test_page
        except BaseException:
            # pytest.fail 使用 BaseException 派生的异常；保证断言失败也有证据。
            try:
                save_failure_screenshot(test_page)
            except Exception as screenshot_error:
                warnings.warn(
                    pytest.PytestWarning(
                        f"失败截图保存失败：{screenshot_error}"
                    )
                )
            raise
        finally:
            browser.close()


def open_homepage(page):
    """打开首页并确认站点可响应。"""
    try:
        response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
    except PlaywrightError as error:
        pytest.fail(f"[环境/站点连接] 无法打开 {BASE_URL}：{error}")

    assert response is not None, "[环境/站点连接] 首页导航没有收到 HTTP 响应"
    assert response.status < 400, (
        f"[站点响应] 首页返回异常状态码：{response.status}"
    )
    assert page.title().strip(), "[页面内容] 首页标题为空"
    assert page.locator("body").inner_text().strip(), "[页面内容] 首页没有可见文本内容"


def add_product_to_cart(page):
    """从商品列表打开现货商品并加入购物车。"""
    product = page.get_by_text(PRODUCT_NAME, exact=True)
    try:
        product.wait_for(state="visible", timeout=15_000)
    except PlaywrightTimeoutError:
        pytest.fail(
            f"[前置条件/数据未就绪] 商品 {PRODUCT_NAME!r} 未在 15 秒内显示；"
            "购物车操作未执行"
        )
    product.click()
    page.get_by_role("button", name="Add to cart").click()


def price_as_decimal(text):
    """从价格文案中解析十进制金额。"""
    normalized = text.strip().replace("$", "").replace(",", "")
    try:
        return Decimal(normalized)
    except InvalidOperation:
        pytest.fail(f"[页面数据] 无法解析金额：{text!r}")


def test_homepage_opens_and_shows_content(page):
    """首页应能打开，并呈现可见的主要内容。"""
    open_homepage(page)


def test_add_product_and_open_cart(page):
    """商品加入后应显示购物车数量，并能在购物车中看到商品。"""
    open_homepage(page)
    add_product_to_cart(page)

    cart_link = page.get_by_role("link", name="cart")
    expect(cart_link).to_have_text("1")

    cart_link.click()
    cart_row = page.locator("tr").filter(has_text=PRODUCT_NAME)
    expect(cart_row).to_have_count(1)
    expect(cart_row.locator("input")).to_have_value("1")


def test_add_to_cart_does_not_show_error(page):
    """确认购物车状态已更新后，成功加入商品不应显示错误提示。"""
    open_homepage(page)
    add_product_to_cart(page)

    cart_link = page.get_by_role("link", name="cart")
    expect(cart_link).to_have_text("1")

    error_alert = page.get_by_role("alert")
    try:
        error_alert.wait_for(state="visible", timeout=2_000)
    except PlaywrightTimeoutError:
        return
    pytest.fail("[功能断言] 加入购物车后页面显示了错误提示")


def test_cart_line_total_matches_price_and_quantity(page):
    """购物车行金额应等于商品单价乘以数量。"""
    open_homepage(page)
    add_product_to_cart(page)
    page.get_by_role("link", name="cart").click()

    cart_row = page.locator("tr").filter(has_text=PRODUCT_NAME)
    expect(cart_row).to_have_count(1)
    price = price_as_decimal(
        cart_row.locator("[data-test='product-price']").inner_text()
    )
    quantity = int(cart_row.locator("input").input_value())
    line_total = price_as_decimal(
        cart_row.locator("[data-test='line-price']").inner_text()
    )
    assert line_total == price * quantity, (
        f"行金额应等于单价 {price} × 数量 {quantity}，实际为 {line_total}"
    )


def test_remove_product_from_cart(page):
    """点击购物车商品行的删除按钮后，商品应从清单中消失。"""
    open_homepage(page)
    add_product_to_cart(page)
    page.get_by_role("link", name="cart").click()

    cart_row = page.locator("tr").filter(has_text=PRODUCT_NAME)
    expect(cart_row).to_have_count(1)

    cart_row.locator("a.btn-danger").click()

    expect(page.locator("tr").filter(has_text=PRODUCT_NAME)).to_have_count(0)
