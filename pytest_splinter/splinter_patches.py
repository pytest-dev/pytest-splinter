"""Patches for splinter."""

from splinter.driver.webdriver import firefox
from splinter.driver.webdriver import phantomjs
from selenium.webdriver.common.action_chains import ActionChains  # pragma: no cover


def patch_webdriverelement():  # pragma: no cover
    """Patche the WebDriverElement to allow firefox to use mouse_over."""
    old_text = phantomjs.WebDriverElement.text

    def text(self):
        """Get element text."""
        text = old_text.fget(self)
        if not text and self.html:
            text = self._element.get_attribute('outerText').strip().replace(u'\xa0', u' ')
        return text

    # Apply the monkey patch for PhantomJs WebDriverElement
    phantomjs.WebDriverElement.text = property(text)
