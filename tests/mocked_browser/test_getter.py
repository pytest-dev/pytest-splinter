"""Browser instance getter tests."""
from pytest_splinter import plugin


def test_browser_instance_getter(browser_instance_getter):
    """Test that browser_instance_getter fixture return function and if run this function then each time we will get
    different instance of plugin.Browser class."""
    assert callable(browser_instance_getter)

    browser1 = browser_instance_getter(test_browser_instance_getter)
    browser2 = browser_instance_getter(lambda: 1)

    assert isinstance(browser1, plugin.Browser)
    assert isinstance(browser2, plugin.Browser)

    assert browser1 is not browser2

    # but if we call it with same parent, the instance should be same
    assert (
        browser_instance_getter(test_browser_instance_getter) is browser_instance_getter(test_browser_instance_getter)
    )
