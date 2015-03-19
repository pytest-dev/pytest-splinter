"""Browser instance getter tests."""
import pytest


@pytest.fixture
def splinter_session_scoped_browser():
    """Override to default to test getter twice."""
    return True


def test_browser_instance_getter(browser_instance_getter):
    """Test browser_instance_getter fixture.

    Test that it return a function and if run this function then each time we will get
    different instance of plugin.Browser class.
    """
    assert callable(browser_instance_getter)

    browser1 = browser_instance_getter(test_browser_instance_getter)
    browser2 = browser_instance_getter(lambda: 1)

    assert hasattr(browser1, 'visit_condition')
    assert hasattr(browser2, 'visit_condition')

    assert browser1 is not browser2

    # but if we call it with same parent, the instance should be same
    assert (
        browser_instance_getter(test_browser_instance_getter) is browser_instance_getter(test_browser_instance_getter)
    )
