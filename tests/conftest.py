"""Configuration for pytest runner."""
import mock

import pytest

pytest_plugins = 'pytester'


@pytest.fixture
def mocked_browser(request):
    """Mock splinter browser."""
    mocked_browser = mock.MagicMock()
    mocked_browser.driver = mock.MagicMock()
    mocked_browser.driver.profile = mock.MagicMock()

    def save_screenshot(path):
        with open(path, 'w'):
            pass

    mocked_browser.driver.save_screenshot = save_screenshot
    patcher = mock.patch('pytest_splinter.plugin.splinter.Browser', lambda *args, **kwargs: mocked_browser)
    request.addfinalizer(patcher.stop)
    patcher.start()
    return mocked_browser
