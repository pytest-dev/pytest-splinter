"""Patches for splinter."""
from functools import partial

from splinter.driver.webdriver import firefox
from splinter.driver.webdriver import phantomjs
from splinter.driver.webdriver import remote

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
    firefox.WebDriverElement.mouse_over = mouse_over

    old_text = phantomjs.WebDriverElement.text

    def text(self):
        """Get element text."""
        text = old_text.fget(self)
        if not text and self.html:
            text = self._element.get_attribute('outerText').strip().replace(u'\xa0', u' ')
        return text

    # Apply the monkey patch for PhantomJs WebDriverElement
    phantomjs.WebDriverElement.text = property(text)
    phantomjs.WebDriverElement.mouse_over = mouse_over
    # Enable keep_alive for remove driver
    remote.Remote = partial(remote.Remote, keep_alive=True)
