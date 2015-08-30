"""Tests for pytest-splinter plugin."""
import os.path
import time
import socket

import pytest

from splinter.driver import DriverAPI
from pytest_splinter.plugin import get_args


@pytest.fixture
def simple_page_content():
    """Simple page content."""
    return """<html xmlns="http://www.w3.org/1999/xhtml"><head></head>
    <body>
        <div id="content">
            <p>
                Some <strong>text</strong>
            </p>
        </div>
        <textarea id="textarea">area text</textarea>
    </body>
</html>"""


@pytest.fixture
def simple_page(httpserver, browser, simple_page_content):
    """Simple served html page."""
    httpserver.serve_content(
        simple_page_content, code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)


def test_browser(browser):
    """Check the browser fixture."""
    assert isinstance(browser, DriverAPI)


def test_session_browser(session_browser):
    """Check the browser fixture."""
    assert isinstance(session_browser, DriverAPI)


def test_status_code(browser, simple_page, splinter_webdriver):
    """Check the browser fixture."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't support status code")
    assert 'status_code' not in browser.__dict__
    assert browser.status_code == 200


@pytest.mark.parametrize(
    (
        'file_extension',
        'mime_type'
    ),
    (
        ['txt', 'text/plain'],
        ['pdf', 'application/pdf'],
    )
)
def test_download_file(httpserver, browser, splinter_file_download_dir, file_extension, mime_type, splinter_webdriver):
    """Test file downloading and accessing it afterwise."""
    if splinter_webdriver in ["zope.testbrowser", "phantomjs"]:
        pytest.skip("{0} doesn't support file downloading".format(splinter_webdriver))
    file_name = 'some.{0}'.format(file_extension)
    httpserver.serve_content(
        'Some text file', code=200, headers={
            'Content-Disposition': 'attachment; filename={0}'.format(file_name),
            'Content-Type': mime_type})
    browser.visit(httpserver.url)
    time.sleep(1)
    assert open(os.path.join(splinter_file_download_dir, file_name)).read() == 'Some text file'


@pytest.mark.parametrize('cookie_name', ['name1', 'name2'])
@pytest.mark.parametrize('splinter_webdriver', ['firefox', 'phantomjs'])
def test_clean_cookies(httpserver, browser, cookie_name, splinter_webdriver, splinter_session_scoped_browser):
    """Test that browser has always clean state (no cookies set)."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't execute js")
    assert not browser.cookies.all()
    httpserver.serve_content(
        """
        <html>
            <body>
                <script>
                    document.cookie = '{name}=value'
                </script>
            </body>
        </html>""".format(name=cookie_name), code=200, headers={'Content-Type': 'text/html'})
    browser.visit(httpserver.url)
    assert browser.cookies.all() == {cookie_name: 'value'}


@pytest.mark.skipif('sys.version_info[0] > 2')
# @pytest.mark.parametrize('splinter_webdriver', ['firefox', 'phantomjs'])
def test_get_text(simple_page, browser, splinter_webdriver):
    """Test that webelement correctly gets text."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't need special text element processing")
    assert browser.find_by_id('content').text == 'Some text'
    assert browser.find_by_id('textarea').text == 'area text'


@pytest.mark.parametrize('check', [1, 2])
@pytest.mark.parametrize('splinter_webdriver', ['firefox', 'remote'])
def test_restore_browser(browser, simple_page, check, splinter_webdriver):
    """Test that browser is restored after failure automatically."""
    if splinter_webdriver == "zope.testbrowser":
        pytest.skip("zope testbrowser doesn't need restore")
    browser.quit()


@pytest.mark.parametrize('splinter_webdriver', ['firefox', 'remote'])
def test_restore_browser_connection(browser, httpserver, simple_page, splinter_webdriver):
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
    arg1 = get_args(driver='phantomjs', executable='/tmp')
    arg2 = get_args(driver='chrome', executable='/tmp')
    assert arg1['executable_path'] == '/tmp'
    assert arg2['executable_path'] == '/tmp'


def test_browser_screenshot_normal(testdir, simple_page_content):
    """Test making screenshots on test failure.

    Normal test run.
    """
    testdir.inline_runsource("""
        import pytest

        @pytest.fixture
        def simple_page(httpserver, browser):
            httpserver.serve_content(
                '''{0}''', code=200, headers={{'Content-Type': 'text/html'}})
            browser.visit(httpserver.url)

        def test_screenshot(simple_page, browser):
            assert False
    """.format(simple_page_content), "-vl", "-r w")

    content = testdir.tmpdir.join('test_browser_screenshot_normal', 'test_screenshot-browser.html').read()
    assert content.replace('\n', '') == simple_page_content.replace('\n', '')
    assert testdir.tmpdir.join('test_browser_screenshot_normal', 'test_screenshot-browser.png')
