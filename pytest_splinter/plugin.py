"""Splinter subplugin for pytest-bdd."""
import copy  # pragma: no cover
import mimetypes  # pragma: no cover

import pytest  # pragma: no cover
import py  # pragma: no cover
import splinter  # pragma: no cover

from .browser_patches import wait_until  # pragma: no cover
from .webdriver_patches import patch_webdriver  # pragma: no cover
from .splinter_patches import patch_webdriverelement  # pragma: no cover


class Browser(object):
    """Emulate splinter's Browser."""

    def __init__(self, *args, **kwargs):
        self.visit_condition = kwargs.pop('visit_condition')
        self.visit_condition_timeout = kwargs.pop('visit_condition_timeout')
        self.browser = splinter.Browser(*args, **kwargs)

    def __getattr__(self, name):
        """Pass every call to splinter's browser."""
        return getattr(self.browser, name)

    def visit(self, url):
        """Override splinter's visit to avoid unnecessary checks and add wait_until instead."""
        self.driver.get(url)
        self.wait_for_condition(self.visit_condition, timeout=self.visit_condition_timeout)

    def wait_for_condition(self, condition=None, timeout=None):
        """Wait for given javascript condition."""
        condition = condition or self.visit_condition
        timeout = timeout or self.visit_condition_timeout
        return wait_until(
            self,
            condition=condition,
            timeout=timeout,
        )


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_close_browser():
    """Close browser fixture."""
    return True


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_webdriver(request):
    """Webdriver fixture."""
    return request.config.option.pytestbdd_webdriver


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_selenium_socket_timeout(request):
    """Internal Selenium socket timeout (communication between webdriver and the browser).
    :return: Seconds.
    """
    return request.config.option.pytestbdd_webdriver_socket_timeout


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_selenium_implicit_wait(request):
    """Selenium implicit wait timeout.
    :return: Seconds.
    """
    return request.config.option.pytestbdd_webdriver_implicit_wait


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_selenium_speed(request):
    """Selenium speed.
    :return: Seconds.
    """
    return request.config.option.pytestbdd_webdriver_speed


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_browser_load_condition():
    """The condition that has to be `True` to assume that the page is fully loaded.

        One example is to wait for jQuery, then the condition could be::

            @pytest.fixture
            def pytestbdd_browser_load_condition():

                def condition(browser):
                    return browser.evaluate_script('typeof $ === "undefined" || !$.active')

                return condition

    """
    return lambda browser: True


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_browser_load_timeout():
    """The timeout in seconds in which the page is expected to be fully loaded."""
    return 10


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_file_download_dir(request):
    """Browser file download directory."""
    name = request.node.name
    name = py.std.re.sub("[\W]", "_", name)
    x = request.config._tmpdirhandler.mktemp(name, numbered=True)

    def finalize():
        x.remove()
    request.addfinalizer(finalize)
    return x.strpath


@pytest.fixture(scope='session')  # pragma: no cover
def pytestbdd_download_file_types():
    """Browser file types to download. Comma-separated"""
    return ','.join(mimetypes.types_map.values())


@pytest.fixture(scope='session')
def pytestbdd_firefox_profile_preferences():
    """Firefox profile preferences."""
    return {
        'browser.cache.memory.enable': False,
        'browser.sessionhistory.max_total_viewers': 0,
        'network.http.pipelining': True,
        'network.http.pipelining.maxrequests': 8
    }


@pytest.fixture(scope='session')
def pytestbdd_driver_kwargs():
    """Webdriver kwargs."""
    return {}


@pytest.fixture(scope='session')
def pytestbdd_window_size():
    """Browser window size. (width, height)."""
    return (1366, 768)


@pytest.fixture  # pragma: no cover
def browser_instance(
    request,
    pytestbdd_selenium_socket_timeout,
    pytestbdd_selenium_implicit_wait,
    pytestbdd_selenium_speed,
    pytestbdd_webdriver,
    pytestbdd_browser_load_condition,
    pytestbdd_browser_load_timeout,
    pytestbdd_file_download_dir,
    pytestbdd_download_file_types,
    pytestbdd_firefox_profile_preferences,
    pytestbdd_driver_kwargs,
    pytestbdd_window_size,
):
    """Splinter browser wrapper instance. To be used for browser interaction."""
    patch_webdriver(pytestbdd_selenium_socket_timeout)
    patch_webdriverelement()

    kwargs = {}

    if pytestbdd_webdriver == 'firefox':
        kwargs['profile_preferences'] = dict({
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir': pytestbdd_file_download_dir,
            'browser.helperApps.neverAsk.saveToDisk': pytestbdd_download_file_types,
            'browser.helperApps.alwaysAsk.force': False,
        }, **pytestbdd_firefox_profile_preferences)
    if pytestbdd_driver_kwargs:
        kwargs.update(pytestbdd_driver_kwargs)
    browser = Browser(
        pytestbdd_webdriver, visit_condition=pytestbdd_browser_load_condition,
        visit_condition_timeout=pytestbdd_browser_load_timeout, **copy.deepcopy(kwargs))
    # set automatic download directory for firefox

    browser.driver.implicitly_wait(pytestbdd_selenium_implicit_wait)
    browser.driver.set_speed(pytestbdd_selenium_speed)
    if pytestbdd_window_size:
        browser.driver.set_window_size(*pytestbdd_window_size)
    return browser


@pytest.fixture(scope='session')
def browser_pool(request, pytestbdd_close_browser):
    """Browser 'pool' to emulate session scope but with possibility to recreate browser."""
    pool = []

    def fin():
        for browser in pool:
            try:
                browser.quit()
            except (IOError, OSError):
                pass

    if pytestbdd_close_browser:
        request.addfinalizer(fin)

    return pool


@pytest.fixture(scope='session')
def pytestbdd_session_scoped_browser(request):
    """Flag to keep single browser per test session."""
    return request.config.option.pytestbdd_session_scoped_browser


@pytest.fixture  # pragma: no cover
def browser(
        request, browser_pool, pytestbdd_webdriver, pytestbdd_session_scoped_browser,
        pytestbdd_close_browser):
    """Splinter browser wrapper instance. To be used for browser interaction.
    Function scoped (cookies are clean for each test and on blank)."""
    get_browser = lambda: request.getfuncargvalue('browser_instance')
    if not pytestbdd_session_scoped_browser:
        browser_pool = []
        browser = get_browser()
        if pytestbdd_close_browser:
            request.addfinalizer(browser.quit)
    elif not browser_pool:
        browser = get_browser()
        browser_pool.append(browser)
    else:
        browser = browser_pool[0]
        try:
            browser.driver.delete_all_cookies()
        except IOError:
            # we lost browser, try to restore the justice
            try:
                browser.quit()
            except Exception:
                pass
            browser = browser_pool[0] = get_browser()

    browser.driver.get('about:blank')
    return browser


def pytest_addoption(parser):  # pragma: no cover
    """Pytest hook to add custom command line option(s)."""
    parser.addoption(
        "--bdd-webdriver",
        help="pytest-bdd-splinter webdriver", type="choice", choices=list(splinter.browser._DRIVERS.keys()),
        dest='pytestbdd_webdriver', default='firefox')

    parser.addoption(
        "--bdd-implicit-wait",
        help="pytest-bdd-splinter selenium implicit wait, seconds", type="int",
        dest='pytestbdd_webdriver_implicit_wait', default=1)

    parser.addoption(
        "--bdd-speed",
        help="pytest-bdd-splinter selenium speed, seconds", type="int",
        dest='pytestbdd_webdriver_speed', default=0)

    parser.addoption(
        "--bdd-socket-timeout",
        help="pytest-bdd-splinter socket timeout, seconds", type="int",
        dest='pytestbdd_webdriver_socket_timeout', default=120)

    parser.addoption(
        "--bdd-session-scoped-browser",
        help="pytest-bdd-splinter should use single browser instance per test session", action="store_true",
        dest='pytestbdd_session_scoped_browser', default=True)
