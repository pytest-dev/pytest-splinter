"""Configuration for pytest runner."""

pytest_plugins = 'pytester'

import mock
import pytest


@pytest.fixture(scope='session')
def splinter_session_scoped_browser():
    """Make it test scoped."""
    return False


@pytest.fixture(autouse=True)
def mocked_browser(request):
    """Mock splinter browser."""
    mocked_browser = mock.MagicMock()
    mocked_browser.driver = mock.MagicMock()
    mocked_browser.driver.profile = mock.MagicMock()
    patcher = mock.patch('pytest_splinter.plugin.splinter.Browser', lambda *args, **kwargs: mocked_browser)
    request.addfinalizer(patcher.stop)
    patcher.start()
    return mocked_browser
