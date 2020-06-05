"""Tests for pytest-splinter django driver availability."""
import pytest
import mock


@pytest.fixture(autouse=True)
def driverless_browser(request):
    """
    Mock splinter browser specifically for driverless browsers.

    Django and Flask browsers extends the LxmlDriver and doesn't provide a
    driver attribute.
    """

    def mocked_browser(driver_name, *args, **kwargs):
        mocked_browser = mock.Mock()
        del mocked_browser.driver  # force AttributeError
        mocked_browser.driver_name = driver_name
        mocked_browser.is_text_present.return_value = True
        return mocked_browser

    with mock.patch("pytest_splinter.plugin.splinter.Browser", mocked_browser):
        yield


@pytest.mark.parametrize("splinter_webdriver", ["django", "flask"])
def test_driverless_splinter_browsers(splinter_webdriver, browser):
    """Test the driverless splinter browsers django and flask."""
    browser.visit("/")
    assert browser.is_text_present("Ok!") is True
