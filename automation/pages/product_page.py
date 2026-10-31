from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError


class ProductPage:
    """商品页面对象，封装商品定位和加入购物车操作。"""

    def __init__(self, page: Page):
        self.page = page

        # 商品详情页的加入购物车按钮
        self.add_to_cart_button = page.get_by_role(
            "button",
            name="Add to cart"
        )

    def open_product(self, product_name):
        """从商品列表打开指定商品。"""
        product = self.page.get_by_text(product_name, exact=True)

        expect(product).to_be_visible(timeout=15_000)
        product.click()

    def add_to_cart(self):
        """将当前商品加入购物车。"""
        self.add_to_cart_button.click()