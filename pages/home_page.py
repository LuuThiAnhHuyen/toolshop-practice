
import re

from pages.base_page import BasePage

# Duong dan API danh sach san pham
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")


class HomePage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)

        self.search_box = page.get_by_test_id("search-query")
        self.search_result_count = page.get_by_test_id("search-result-count")

        # B1.1: Tim kiem san pham
        self.search_button = page.get_by_test_id("search-submit")
        self.search_caption = page.get_by_test_id("search-caption")
        self.search_completed = page.get_by_test_id("search_completed")
        self.product_names = page.get_by_test_id("product-name")

        # B1.2: Khong tim thay san pham
        self.no_results = page.get_by_test_id("no-results")

        # B1.7: Sap xep san pham
        self.sort_select = page.get_by_test_id("sort")
        self.sorting_completed = page.get_by_test_id("sorting_completed")
        self.product_prices = page.get_by_test_id("product-price")

        # TODO B2/B4: Bai hoc sau
        # price_slider_max = page.get_by_role("slider").nth(1)

    def open(self):
        with self.page.expect_response(
            lambda r: PRODUCT_LIST.search(r.url) is not None
        ):
            super().open()
        return self

    # B1.1: Tim kiem
    def search(self, keyword: str):
        self.search_box.fill(keyword)
        self.search_button.click()
        return self

    # B1.7: Sap xep
    def sort_by(self, value: str):
        """name,asc | name,desc | price,asc | price,desc"""
        self.sort_select.select_option(value)
        return self

    # Tim san pham theo ten
    def product_card(self, name: str):
        return self.product_names.filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )

    # B1.3: Mo chi tiet san pham
    def open_product(self, name: str):
        from pages.product_page import ProductPage

        self.product_card(name).first.click()
        return ProductPage(self.page)

    # B1.7: Lay gia san pham
    def prices(self) -> list[float]:
        return [
            float(p.replace("$", ""))
            for p in self.product_prices.all_inner_texts()
        ]
