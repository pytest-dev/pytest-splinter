"""Tests for pytest-splinter django driver availability."""
import pytest


@pytest.mark.parametrize("splinter_webdriver", ["django"])
@pytest.mark.django
def test_django_client(splinter_webdriver, browser):
    """
    Test the availability of django driver by testing hit the admin.
    """
    browser.visit("/admin/")
    assert browser.is_text_present("Django administration")
