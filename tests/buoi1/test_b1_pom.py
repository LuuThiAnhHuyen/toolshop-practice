
"""Buoi 1 - Page Object Model exercises."""

import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.login_page import LoginPage


# B1.1 - Tim kiem san pham
@pytest.mark.smoke
@pytest.mark.ui
def test_b1_1_search_keyword_shows_only_matching_products(page):
    """Goal: search filters the grid.
    Precondition: none.
    Expected: every product name contains the keyword."""
    home = HomePage(page).open().search("pliers")

    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")

    names = home.product_names.all_inner_texts()
    assert names, "Search returned no products"
    assert all("pliers" in n.lower() for n in names)


# B1.2 - Tim kiem khong co ket qua
def test_b1_2_search_unknown_keyword_shows_no_results_message(page):
    """Goal: check search with unknown keyword.
    Precondition: none.
    Expected: no products found and zero product cards."""
    home = HomePage(page).open().search("zzz-no-such-tool")

    expect(home.search_completed).to_be_visible()
    expect(home.no_results).to_contain_text(
        "There are no products found."
    )
    expect(home.product_names).to_have_count(0)


# B1.3 - Them 3 san pham vao gio
def test_b1_3_product_add_quantity_three_updates_cart_badge(page):
    """Goal: add three products to cart.
    Precondition: Claw Hammer exists.
    Expected: success message and cart quantity 3."""
    product = HomePage(page).open().open_product("Claw Hammer")

    expect(product.name).to_contain_text("Claw Hammer")
    product.add_to_cart(quantity=3)

    expect(product.toast).to_contain_text(
        "Product added to shopping cart"
    )
    expect(product.cart_quantity).to_have_text("3")


# B1.4 - Kiem tra tinh tien
def test_b1_4_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: verify cart calculation.
    Precondition: empty cart.
    Expected: line price equals unit price times quantity."""
    product = HomePage(page).open().open_product("Claw Hammer")

    unit_price = product.price()

    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")

    cart = product.go_to_cart()

    expect(cart.product_titles).to_contain_text(["Claw Hammer"])

    line_totals = cart.line_totals()

    assert len(line_totals) == 1
    assert line_totals[0] == pytest.approx(unit_price * 2)
    assert cart.total_value() == pytest.approx(sum(line_totals))


# B1.5 - Dang nhap sai
def test_b1_5_login_wrong_password_shows_error(page):
    """Goal: reject wrong login credentials.
    Precondition: email does not belong to a shared account.
    Expected: invalid credentials error and stay on login page."""
    login = LoginPage(page).open()

    login.login(
        "nobody-here@example.com",
        "Wrong-Password-123"
    )

    expect(login.error).to_contain_text(
        "Invalid email or password"
    )

    # Kiem tra URL van o trang dang nhap
    expect(page).to_have_url(
        re.compile(r"/auth/login$")
    )


# B1.5 - Bo trong thong tin dang nhap
def test_b1_5_login_empty_form_shows_required_errors(page):
    """Goal: validate empty login form.
    Precondition: none.
    Expected: email and password required errors."""
    login = LoginPage(page).open()

    login.login("", "")

    expect(login.email_error).to_contain_text(
        "Email is required"
    )
    expect(login.password_error).to_contain_text(
        "Password is required"
    )


# B1.6 - Tiep tuc mua hang
def test_b1_6_cart_continue_shopping_returns_to_home(page):
    """Goal: return to home from cart.
    Precondition: product has been added to cart.
    Expected: product grid is visible again."""
    product = HomePage(page).open().open_product("Claw Hammer")

    product.add_to_cart()
    expect(product.cart_quantity).to_have_text("1")

    cart = product.go_to_cart()
    home = cart.continue_shopping_to_home()

    expect(home.product_names.first).to_be_visible()


# B1.7 - Sap xep theo gia
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_b1_7_sort_by_price_orders_products(page, order):
    """Goal: verify product sorting.
    Precondition: none.
    Expected: prices sorted ascending or descending."""
    home = HomePage(page).open()
    home.sort_by(order)

    expect(home.sorting_completed).to_be_visible()

    prices = home.prices()
    assert prices, "No products found"

    reverse = order == "price,desc"

    assert prices == sorted(prices, reverse=reverse)
