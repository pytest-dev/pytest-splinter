"""Configuration for pytest runner."""

pytest_plugins = 'pytester'

import pytest


@pytest.fixture(scope='session')
def splinter_session_scoped_browser():
    """Make it test scoped."""
    return False


@pytest.fixture(autouse=True)
def mocked_browser(mocked_browser):
    """Make mocked browser fixture autoused."""
    return mocked_browser
