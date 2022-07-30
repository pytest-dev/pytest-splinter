"""Patches for splinter."""
from functools import partial

from splinter.driver import webdriver

from selenium.webdriver.common.action_chains import ActionChains  # pragma: no cover


def patch_webdriverelement():  # pragma: no cover
    """Patch the WebDriverElement to allow firefox to use mouse_over."""

    def mouse_over(self):
        """Perform a mouse over the element which works."""
        (
            ActionChains(self.parent.driver)
            .move_to_element_with_offset(self._element, 2, 2)
            .perform()
        )

    # Apply the monkey patch for Firefox WebDriverElement
    try:
        webdriver.firefox.WebDriverElement.mouse_over = mouse_over
    except AttributeError:
        # With splinter 0.18.1 it could be made easier, as the web_element_class
        # is in the initializer, but ATM it is not, so we should patch it
        # globally. Will it hurt in the long run? The function is pretty similar
        # to the one in splinter... as long as the element we try to mouse_over
        # is at least 2 pixels wide...
        webdriver.WebDriverElement.mouse_over = mouse_over
