"""Selenium webdriver monkey patches.

Patches are temporary fixes for issues raised in we selenium google project:
http://code.google.com/p/selenium/issues/detail?id=5175
http://code.google.com/p/selenium/issues/detail?id=5176.
"""

import time  # pragma: no cover
import socket  # pragma: no cover
try:
    from httplib import HTTPException
except ImportError:
    from http.client import HTTPException

import urllib3
from urllib3.exceptions import MaxRetryError

from selenium.webdriver.remote import remote_connection  # pragma: no cover
from selenium.webdriver.firefox import webdriver  # pragma: no cover
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver  # pragma: no cover


# Get the original _request and store for future use in the monkey patched version as 'super'
old_request = remote_connection.RemoteConnection._request  # pragma: no cover
# save the original execute
RemoteWebDriver._base_execute = RemoteWebDriver.execute  # pragma: no cover

old_init = RemoteWebDriver.__init__  # pragma: no cover


def __init__(self, *args, **kwargs):
    """Set keep_alive to True."""
    kwargs['keep_alive'] = True
    return old_init(self, *args, **kwargs)


def patch_webdriver():
    """Patch selenium webdriver to add functionality/fix issues."""
    def _request(self, *args, **kwargs):
        """Override _request to set socket timeout to some appropriate value."""
        exception = HTTPException('Unable to get response')
        for _ in range(3):
            try:
                return old_request(self, *args, **kwargs)
            except (socket.error, HTTPException, IOError, OSError, MaxRetryError) as exc:
                exception = exc
                self._conn = urllib3.PoolManager(timeout=self._timeout)
        raise exception

    # Apply the monkey patch for RemoteConnection
    remote_connection.RemoteConnection._request = _request

    # Apply the monkey patch to Firefox webdriver to disable native events
    # to avoid click on wrong elements, totally unpredictable
    # more info http://code.google.com/p/selenium/issues/detail?id=633
    webdriver.WebDriver.NATIVE_EVENTS_ALLOWED = False

    def execute(self, driver_command, params=None):
        result = self._base_execute(driver_command, params)
        speed = self.get_speed()
        if speed > 0:
            time.sleep(speed)  # pragma: no cover
        return result

    def get_current_window_info(self):
        atts = self.execute_script("return [ window.id, window.name, document.title, document.url ];")
        atts = [
            att if att is not None and att else 'undefined'
            for att in atts]
        return (self.current_window_handle, atts[0], atts[1], atts[2], atts[3])

    def current_window_is_main(self):
        return self.current_window_handle == self.window_handles[0]

    def set_speed(self, seconds):
        self._speed = seconds

    def get_speed(self):
        if not hasattr(self, '_speed'):
            self._speed = float(0)
        return self._speed

    RemoteWebDriver.set_speed = set_speed
    RemoteWebDriver.get_speed = get_speed
    RemoteWebDriver.execute = execute
    RemoteWebDriver.get_current_window_info = get_current_window_info
    RemoteWebDriver.current_window_is_main = current_window_is_main
    RemoteWebDriver.__init__ = __init__
