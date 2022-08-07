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


def test_speed(browser, splinter_webdriver):
    """Test browser's driver set_speed and get_speed."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't need the speed")
    browser.driver.set_speed(2)
    assert browser.driver.get_speed() == 2


def test_get_current_window_info(browser, splinter_webdriver):
    """Test browser's driver get_current_window_info."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't have windows")
    assert len(browser.driver.get_current_window_info()) == 5


def test_current_window_is_main(browser, splinter_webdriver):
    """Test browser's driver current_window_is_main."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't have windows")
    assert browser.driver.current_window_is_main()


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


def test_browser_screenshot_normal(testdir, simple_page_content):
    """Test making screenshots on test failure.

    Normal test run.
    """
    testdir.inline_runsource(
        """
import pytest

@pytest.fixture
def simple_page(httpserver, browser):
    httpserver.serve_content(
        '''{0}''', code=200, headers={{'Content-Type': 'text/html'}})
    browser.visit(httpserver.url)

def test_screenshot(simple_page, browser):
    assert False
    """.format(
            simple_page_content
        ),
        "-vl",
        "-r w",
    )

    assert testdir.tmpdir.join(
        "test_browser_screenshot_normal", "test_screenshot-browser.png"
    )
    content = testdir.tmpdir.join(
        "test_browser_screenshot_normal", "test_screenshot-browser.html"
    ).read()
    assert_valid_html_screenshot_content(content)


def test_browser_screenshot_function_scoped_browser(testdir, simple_page_content):
    """Test making screenshots on test failure.

    Normal test run.
    """
    testdir.inline_runsource(
        """
import pytest

@pytest.fixture
def simple_page(httpserver, browser):
    httpserver.serve_content(
        '''{0}''', code=200, headers={{'Content-Type': 'text/html'}})
    browser.visit(httpserver.url)

def test_screenshot(simple_page, browser):
    assert False
    """.format(
            simple_page_content
        ),
        "-vl",
        "-r w",
        "--splinter-session-scoped-browser=false",
    )

    content = testdir.tmpdir.join(
        "test_browser_screenshot_function_scoped_browser",
        "test_screenshot-browser.html",
    ).read()

    assert_valid_html_screenshot_content(content)
    assert testdir.tmpdir.join(
        "test_browser_screenshot_normal", "test_screenshot-browser.png"
    )


def test_browser_screenshot_escaped(testdir, simple_page_content):
    """Test making screenshots on test failure with escaped test names.

    Normal test run.
    """
    testdir.inline_runsource(
        """
import pytest

@pytest.fixture
def simple_page(httpserver, browser):
    httpserver.serve_content(
        '''{0}''', code=200, headers={{'Content-Type': 'text/html'}})
    browser.visit(httpserver.url)

@pytest.mark.parametrize('param', ['escaped/param'])
def test_screenshot(simple_page, browser, param):
    assert False
    """.format(
            simple_page_content
        ),
        "-vl",
        "-r w",
    )

    content = testdir.tmpdir.join(
        "test_browser_screenshot_escaped", "test_screenshot[escaped-param]-browser.html"
    ).read()
    assert_valid_html_screenshot_content(content)
    assert testdir.tmpdir.join(
        "test_browser_screenshot_escaped", "test_screenshot[escaped-param]-browser.png"
    )


@pytest.mark.parametrize("splinter_webdriver", ["remote"])
def test_keep_alive(simple_page, browser, splinter_webdriver):
    """Test that Remote WebDriver keep_alive is True."""
    if splinter_webdriver != "remote":
        pytest.skip("Only Remote WebDriver uses keep_alive argument")

    assert browser.driver.keep_alive
