"""Browser screenshot tests."""
import pytest


def test_browser_screenshot_normal(testdir, mocked_browser):
    """Test making screenshots on test failure if the commandline option is passed.

    Normal test run.
    """
    testdir.inline_runsource("""
        def test_screenshot(browser):
            assert False
    """, "-vl", "--splinter-session-scoped-browser=false")

    assert testdir.tmpdir.join('test_browser_screenshot_normal', 'test_screenshot-browser.png').isfile()


def test_browser_screenshot_error(testdir, mocked_browser):
    """Test warning with error during taking screenshots on test failure."""
    testdir.makepyfile("""
        def test_screenshot(browser):
            # Create a file here, so makedirs in make_screenshot_on_failure will fail.
            open('isafile', 'w').close()
            assert False
    """)
    result = testdir.runpytest('-sv', "--splinter-screenshot-dir=isafile",
                               '-rw')

    result.stdout.fnmatch_lines([
        '*test_screenshot FAILED*',
        'Wsplinter None Could not save screenshot: * Not a directory*'
    ])
    assert '*test_screenshot ERROR*' not in result.stdout.str()

    assert result.ret != 0


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
