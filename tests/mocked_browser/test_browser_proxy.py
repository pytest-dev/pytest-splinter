import time

import pytest

from pytest_splinter import plugin


def test_wait_for_condition(
    browser,
    splinter_browser_load_condition,
    splinter_browser_load_timeout,
):
    """Test that by default wait_until is successful."""
    browser.wait_for_condition(
        splinter_browser_load_condition,
        splinter_browser_load_timeout,
    )
    assert True


def test_wait_for_condition_timeout(
    browser,
    monkeypatch,
):
    """Check timeouts."""
    ticks = iter([1, 2, 15])

    def fake_time():
        return next(ticks)

    monkeypatch.setattr(time, 'time', fake_time)

    pytest.raises(Exception, browser.wait_for_condition, (lambda browser: False), 10)


def test_wait_for_condititon(browser, monkeypatch, mocked_browser):
    """Check conditioning."""
    checks = iter([False, True])

    def condition(browser):
        assert isinstance(browser, plugin.Browser)
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

    assert sleeps == [0.5]