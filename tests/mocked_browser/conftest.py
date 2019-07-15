"""Configuration for pytest runner."""
import mock

import pytest


@pytest.fixture(scope='session')
def splinter_session_scoped_browser():
    """Make it test scoped."""
    return False


@pytest.yield_fixture(autouse=True)
def mocked_browser(browser_pool, request):
    """Mock splinter browser."""
    # to avoid re-using of cached browser from other tests
    for browser in browser_pool.values():
        browser.quit()
    browser_pool.clear()

    def mocked_browser(driver_name, *args, **kwargs):
        mocked_browser = mock.MagicMock()
        mocked_browser.driver = mock.MagicMock()
        mocked_browser.driver.profile = mock.MagicMock()
        mocked_browser.driver_name = driver_name
        mocked_browser.html = u'<html></html>'

        def screenshot(path):
            filename = '{}.png'.format(path)
            with open(filename, 'w'):
                pass
            return filename

        mocked_browser.screenshot = screenshot
        return mocked_browser

    patcher = mock.patch('pytest_splinter.plugin.splinter.Browser', mocked_browser)
    yield patcher.start()
    patcher.stop()
