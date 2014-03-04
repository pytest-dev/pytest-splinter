"""Tests for pytest-bdd-splinter subplugin."""
import os.path

import pytest

from pytest_splinter import plugin


def test_browser(browser):
    """Check the browser fixture."""
    assert isinstance(browser, plugin.Browser)


def test_download_file(httpserver, browser, splinter_file_download_dir):
    """Test file downloading and accessing it afterwise."""
    httpserver.serve_content(
        'Some text file', code=200, headers={
            'Content-Disposition': 'attachment; filename=some.txt',
            'Content-Type': 'text/plain'})
    browser.visit(httpserver.url)
    assert open(os.path.join(splinter_file_download_dir, 'some.txt')).read() == 'Some text file'


@pytest.mark.parametrize('cookie_value', ['value1', 'value2'])
def test_clean_cookies(httpserver, browser, cookie_value):
    """Test that browser has always clean state (no cookies set)."""
    assert browser.driver.get_cookie('test') is None
    httpserver.serve_content(
        """
        <html>
            <body>
                <script>
                    document.cookie = 'test=value'
                </script>
            </body>
        </html>""", code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)
    assert browser.driver.get_cookie('test')


@pytest.mark.skipif('sys.version_info[0] > 2')
@pytest.mark.parametrize('splinter_webdriver', ['firefox', 'phantomjs'])
def test_get_text(httpserver, browser, splinter_webdriver):
    """Test that webelement correctly gets text."""
    httpserver.serve_content(
        """
        <html>
            <body>
                <div id="content">
                    <p>
                        Some <strong>text</strong>
                    </p>
                </div>
                <textarea id="textarea">area text</textarea>
            </body>
        </html>""", code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)
    assert browser.find_by_id('content').text == 'Some text'
    assert browser.find_by_id('textarea').text == 'area text'


@pytest.mark.parametrize('check', [1, 2])
def test_restore_browser(browser, httpserver, check):
    httpserver.serve_content(
        """
        <html>
            <body>
                <div id="content">
                    <p>
                        Some <strong>text</strong>
                    </p>
                </div>
                <textarea id="textarea">area text</textarea>
            </body>
        </html>""", code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)
    browser.quit()


def test_speed(browser):
    """Test browser's driver set_speed and get_speed."""
    browser.driver.set_speed(2)
    assert browser.driver.get_speed() == 2


def test_get_current_window_info(browser):
    """Test browser's driver get_current_window_info."""
    assert len(browser.driver.get_current_window_info()) == 5


def test_current_window_is_main(browser):
    """Test browser's driver current_window_is_main."""
    assert browser.driver.current_window_is_main()
