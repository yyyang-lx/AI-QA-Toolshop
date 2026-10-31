"""With Bugs 网站首页和购物车 UI 自动化测试。"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import warnings

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect, sync_playwright
from automation.pages.cart_page import CartPage
from automation.pages.product_page import ProductPage
from automation.pages.home_page import HomePage

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
    """打开并检查网站首页。"""
    home_page = HomePage(page)
    home_page.open(BASE_URL)


def add_product_to_cart(page):
    """从商品列表打开指定商品，并将其加入购物车。"""
    product_page = ProductPage(page)
    product_page.open_product(PRODUCT_NAME)
    product_page.add_to_cart()


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

    cart_page = CartPage(page)

    expect(cart_page.cart_link).to_have_text("1")

    cart_page.open()
    cart_page.expect_product_visible(PRODUCT_NAME)

    cart_row = cart_page.get_product_row(PRODUCT_NAME)
    expect(cart_row.locator("input")).to_have_value("1")


def test_add_to_cart_does_not_show_error(page):
    """确认购物车状态已更新后，成功加入商品不应显示错误提示。"""
    open_homepage(page)
    add_product_to_cart(page)

    cart_page = CartPage(page)
    expect(cart_page.cart_link).to_have_text("1")

    error_alert = cart_page.get_error_alert()
    try:
        error_alert.wait_for(state="visible", timeout=2_000)
    except PlaywrightTimeoutError:
        return
    pytest.fail("[功能断言] 加入购物车后页面显示了错误提示")


def test_cart_line_total_matches_price_and_quantity(page):
    """购物车行金额应等于商品单价乘以数量。"""
    open_homepage(page)
    add_product_to_cart(page)
    cart_page = CartPage(page)
    cart_page.open()

    cart_page.expect_product_visible(PRODUCT_NAME)

    # 使用 CartPage 中封装的方法获取数据
    price = price_as_decimal(cart_page.get_product_price(PRODUCT_NAME))
    quantity = int(cart_page.get_product_quantity(PRODUCT_NAME))
    line_total = price_as_decimal(cart_page.get_product_line_total(PRODUCT_NAME))

    assert line_total == price * quantity, (
        f"行金额应等于单价 {price} × 数量 {quantity}，实际为 {line_total}"
    )


def test_remove_product_from_cart(page):
    """点击购物车商品行的删除按钮后，商品应从清单中消失。"""
    open_homepage(page)
    add_product_to_cart(page)
    cart_page = CartPage(page)
    cart_page.open()

    cart_page.expect_product_visible(PRODUCT_NAME)
    cart_page.remove_product(PRODUCT_NAME)
    cart_page.expect_product_removed(PRODUCT_NAME)
