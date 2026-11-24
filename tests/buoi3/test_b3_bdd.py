
"""Buoi 3 - BDD Automation Testing with pytest-bdd."""

import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

# BDD features
scenarios("search.feature", "cart.feature")


# =========================================================
# GIVEN - Open home page
# =========================================================

@given("I am on the home page", target_fixture="home")
def home(page):
    home_page = HomePage(page).open()
    expect(home_page.product_names.first).to_be_visible()
    return home_page


# =========================================================
# B3.1 - B3.2: PRODUCT SEARCH
# =========================================================

@when(parsers.parse('I search for "{keyword}"'))
def search(home, keyword):
    home.search(keyword)


@then(parsers.parse('every product name contains "{keyword}"'))
def names_contain(home, keyword):
    expect(home.search_completed).to_be_visible()

    names = home.product_names.all_inner_texts()

    assert names, "No products were found"
    assert all(
        keyword.lower() in name.lower()
        for name in names
    ), names


@then(parsers.parse('the search caption mentions "{keyword}"'))
def search_caption_mentions(home, keyword):
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text(keyword)


@then(parsers.parse('I see the message "{message}"'))
def see_empty_message(home, message):
    expect(home.search_completed).to_be_visible()
    expect(home.no_results).to_contain_text(message)


# =========================================================
# B3.3 - B3.4: SHOPPING CART
# =========================================================

@when(
    parsers.parse('I open the product "{product}"'),
    target_fixture="product_page"
)
def open_product(home, product):
    product_page = home.open_product(product)
    expect(product_page.unit_price).to_be_visible()
    return product_page


@when(
    parsers.parse(
        "I add it to the cart with quantity {quantity:d}"
    ),
    target_fixture="cart_context"
)
def add_product_to_cart(product_page, quantity):
    unit_price = product_page.price()

    product_page.add_to_cart(quantity)

    cart = product_page.go_to_cart()

    expect(cart.total).to_be_visible()

    return {
        "cart": cart,
        "unit_price": unit_price,
        "quantity": quantity,
    }


@then(
    parsers.parse(
        "the cart line price equals the unit price times {quantity:d}"
    )
)
def verify_line_price(cart_context, quantity):
    cart = cart_context["cart"]
    unit_price = cart_context["unit_price"]

    assert quantity == cart_context["quantity"]

    line_totals = cart.line_totals()

    assert len(line_totals) == 1

    expected_price = unit_price * quantity

    assert line_totals[0] == pytest.approx(
        expected_price, abs=0.01
    )


@then("the cart total equals the sum of the line prices")
def verify_cart_total(cart_context):
    cart = cart_context["cart"]

    expected_total = sum(cart.line_totals())
    actual_total = cart.total_value()

    assert actual_total == pytest.approx(
        expected_total, abs=0.01
    )
