import time

import pytest

import mock
import splinter

from pytest_splinter.browser_patches import WaitUntilTimeout
from pytest_splinter import plugin


def setup_module():
    """Mock splinter browser."""
    mocked_browser = mock.MagicMock()
    mocked_browser.driver = mock.MagicMock()
    mocked_browser.driver.profile = mock.MagicMock()
    splinter._Browser = splinter.Browser
    splinter.Browser = lambda *args, **kwargs: mocked_browser


def teardown_module():
    """Unmock browser back."""
    splinter.Browser = splinter._Browser


@pytest.fixture
def browser_pool():
    """Browser fixture. Overriden to make it test-scoped and mock."""
    return []


def test_wait_for_condition(
    browser,
    pytestbdd_browser_load_condition,
    pytestbdd_browser_load_timeout,
):
    """Test that by default wait_until is successful."""
    assert browser.wait_for_condition(
        pytestbdd_browser_load_condition,
        pytestbdd_browser_load_timeout,
    )


def test_wait_for_condition_timeout(
    browser,
    monkeypatch,
):
    """Check timeouts."""
    ticks = iter([1, 2, 15])

    def fake_time():
        return next(ticks)

    monkeypatch.setattr(time, 'time', fake_time)

    pytest.raises(WaitUntilTimeout, browser.wait_for_condition, (lambda browser: False), 10)


def test_wait_for_condititon(browser, monkeypatch):
    """Check conditioning."""
    checks = iter([False, True])

    def condition(browser):
        return next(checks)

    ticks = iter([1, 2, 3])

    def fake_time():
        return next(ticks)

    sleeps = []

    def fake_sleep(i):
        sleeps.append(i)

    monkeypatch.setattr(time, 'time', fake_time)
    monkeypatch.setattr(time, 'sleep', fake_sleep)

    assert browser.wait_for_condition(condition, 10)

    assert sleeps == [0.1]
