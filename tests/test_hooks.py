import os

from .utils import assert_valid_html_screenshot_content


def test_hooks_screenshot_dir(testdir, simple_page_content):
    """Test the pytest_splinter_screenshor_dir hook.

    Overriding this hook should change where test screenshots are saved.
    """
    testdir.makeconftest(
        """
import pytest


def pytest_splinter_screenshot_dir(config):
    return "tester_root_screenshot_dir"

        """

    )
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
    """.format(simple_page_content), "-vl", "-r w")

    screenshot_path = testdir.tmpdir.join(
        'tester_root_screenshot_dir',
        'test_hooks_screenshot_dir',
        'test_screenshot-browser.png'
    )
    assert os.path.exists(str(screenshot_path))

    content = testdir.tmpdir.join(
        'tester_root_screenshot_dir',
        'test_hooks_screenshot_dir',
        'test_screenshot-browser.html').read()
    assert_valid_html_screenshot_content(content)
