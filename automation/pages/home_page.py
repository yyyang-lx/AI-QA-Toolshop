import pytest

from playwright.sync_api import Page, Error as PlaywrightError


class HomePage:
    """首页页面对象，封装首页导航和页面检查。"""

    def __init__(self, page: Page):
        self.page = page

    def open(self, url):
        """打开网站首页并检查页面是否正常加载。"""
        try:
            response = self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60_000
            )
        except PlaywrightError as error:
            pytest.fail(f"[环境/站点连接] 无法打开 {url}：{error}")

        assert response is not None, (
            "[环境/站点连接] 首页导航没有收到 HTTP 响应"
        )

        assert response.status < 400, (
            f"[站点响应] 首页返回异常状态码：{response.status}"
        )

        assert self.page.title().strip(), (
            "[页面内容] 首页标题为空"
        )

        assert self.page.locator("body").inner_text().strip(), (
            "[页面内容] 首页没有可见文本内容"
        )