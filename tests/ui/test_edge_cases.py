import pytest
from playwright.sync_api import expect

from helpers import wait_for_shiny_idle


@pytest.fixture
def app_page(page, base_url):
    page.goto(base_url)
    expect(page.locator("#submit")).to_be_visible()
    wait_for_shiny_idle(page)
    return page


def test_empty_name_shows_error(app_page):
    app_page.fill("#age", "30")
    app_page.click("#submit")
    wait_for_shiny_idle(app_page)
    expect(app_page.locator("#error_msg")).to_contain_text("Name is required")
    expect(app_page.locator("#greeting")).to_be_empty()


def test_invalid_age_shows_error(app_page):
    app_page.fill("#user_name", "Alice")
    app_page.fill("#age", "500")
    app_page.click("#submit")
    wait_for_shiny_idle(app_page)
    expect(app_page.locator("#error_msg")).to_contain_text("Age must be between 1 and 120")


def test_valid_submit_shows_greeting(app_page):
    app_page.fill("#user_name", "Alice")
    app_page.fill("#age", "30")
    app_page.click("#submit")
    wait_for_shiny_idle(app_page)
    expect(app_page.locator("#greeting")).to_contain_text("Hello, Alice")
    expect(app_page.locator("#error_msg")).to_be_empty()
