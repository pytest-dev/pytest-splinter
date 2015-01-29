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

    def mocked_browser(*args, **kwargs):
        mocked_browser = mock.MagicMock()
        mocked_browser.driver = mock.MagicMock()
        mocked_browser.driver.profile = mock.MagicMock()

        def save_screenshot(path):
            with open(path, 'w'):
                pass

        mocked_browser.driver.save_screenshot = save_screenshot
        return mocked_browser

    patcher = mock.patch('pytest_splinter.plugin.splinter.Browser', mocked_browser)
    patcher.start()
    yield mocked_browser
    patcher.stop()
