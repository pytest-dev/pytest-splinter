"""Browser screenshot tests."""
import pytest

from mock import patch


def test_browser_screenshot_normal(testdir, mocked_browser):
    """Test making screenshots on test failure if the commandline option is passed.

    Normal test run.
    """
    testdir.inline_runsource("""
        def test_screenshot(browser):
            assert False
    """, "-vl", "--splinter-session-scoped-browser=false")

    assert testdir.tmpdir.join('test_browser_screenshot_normal', 'test_screenshot-browser.png').isfile()


@patch('_pytest.config.Config.warn')
def test_browser_screenshot_error(testdir, mocked_browser):
    """Test warning with error during taking screenshots on test failure."""
    testdir.inline_runsource("""
        def test_screenshot(browser):
            # Create a file here, so makedirs in make_screenshot_on_failure will fail.
            open('isafile', 'w').close()
            assert False

        def test_warn_called(request):
            assert request.config.warn.call_count == 1
    """, "-vl", "--splinter-session-scoped-browser=false")


@pytest.mark.skipif('not config.pluginmanager.getplugin("xdist")', reason='pytest-xdist is not installed')
def test_browser_screenshot_xdist(testdir, mocked_browser):
    """Test making screenshots on test failure if the commandline option is passed.

    Distributed test run.
    """
    testdir.inline_runsource("""
        def test_screenshot(browser):
            assert False
    """, "-vl", "-n1")

    assert testdir.tmpdir.join('test_browser_screenshot_xdist', 'test_screenshot-browser.png').isfile()
