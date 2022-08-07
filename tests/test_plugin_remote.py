"""Tests for pytest-splinter plugin."""
import os.path
import time
import socket

import pytest

from splinter.driver import DriverAPI
from pytest_splinter.plugin import get_args



@pytest.mark.parametrize("check", [1, 2])
@pytest.mark.parametrize("splinter_webdriver", ["remote"])
def test_restore_browser(browser, simple_page, check, splinter_webdriver):
    """Test that browser is restored after failure automatically."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't need restore")
    browser.quit()


@pytest.mark.parametrize("splinter_webdriver", ["remote"])
def test_restore_browser_connection(
    browser, httpserver, simple_page, splinter_webdriver
):
    """Test that browser connection is restored after failure automatically."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't need restore")

    def raises(*args, **kwargs):
        raise socket.error()

    browser.driver.command_executor._conn.request = raises
    browser.reload()

def test_executable():
    """Test argument construction for webdrivers."""
    arg1 = get_args(driver="chrome", executable="/tmp")
    assert arg1["executable_path"] == "/tmp"


def assert_valid_html_screenshot_content(content):
    """Make sure content fetched from html screenshoting looks correct."""
    assert content.startswith('<html xmlns="http://www.w3.org/1999/xhtml">')
    assert '<div id="content">' in content
    assert "<strong>text</strong>" in content
    assert content.endswith("</html>")


@pytest.mark.parametrize("splinter_webdriver", ["remote"])
def test_keep_alive(simple_page, browser, splinter_webdriver):
    """Test that Remote WebDriver keep_alive is True."""
    if splinter_webdriver != "remote":
        pytest.skip("Only Remote WebDriver uses keep_alive argument")
    assert browser.driver.command_executor.keep_alive
