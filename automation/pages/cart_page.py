
from playwright.sync_api import Page, expect


class CartPage:
    """购物车页面对象，封装购物车页面的定位和操作。"""

    def __init__(self, page: Page):
        self.page = page

        # 购物车入口
        self.cart_link = page.get_by_role("link", name="cart")

        # 购物车中的商品行
        self.product_rows = page.locator("tr")

    def open(self):
        """打开购物车页面。"""
        self.cart_link.click()

    def get_product_row(self, product_name):
        """定位指定商品所在的购物车行。"""
        return self.product_rows.filter(
            has=self.page.get_by_text(product_name, exact=True)
        )

    def expect_product_visible(self, product_name):
        """验证指定商品存在于购物车中。"""
        expect(self.get_product_row(product_name)).to_have_count(1)

    def expect_product_removed(self, product_name):
        """验证指定商品已经从购物车中移除。"""
        expect(self.get_product_row(product_name)).to_have_count(0)

    def remove_product(self, product_name):
        """点击指定商品行中的删除元素。"""
        row = self.get_product_row(product_name)
        remove_link = row.locator("a.btn-danger")

        expect(remove_link).to_have_count(1)
        remove_link.click()
        
    def get_error_alert(self):
        """获取页面中的错误提示元素。"""
        return self.page.get_by_role("alert")

    def get_product_price(self, product_name):
        """获取指定商品的单价文本。"""
        row = self.get_product_row(product_name)
        return row.locator("[data-test='product-price']").inner_text()

    def get_product_quantity(self, product_name):
        """获取指定商品的数量输入框的值。"""
        row = self.get_product_row(product_name)
        return row.locator("input").input_value()

    def get_product_line_total(self, product_name):
        """获取指定商品的行总价文本。"""
        row = self.get_product_row(product_name)
        return row.locator("[data-test='line-price']").inner_text()