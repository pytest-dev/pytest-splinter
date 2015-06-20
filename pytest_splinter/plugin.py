"""Splinter plugin for pytest.

Provides easy interface for the browser from your tests providing the `browser` fixture
which is an object of splinter Browser class.
"""
import functools  # pragma: no cover
try:
    from httplib import HTTPException
except ImportError:
    from http.client import HTTPException

import mimetypes  # pragma: no cover
import os.path
import re

import pytest  # pragma: no cover
import splinter  # pragma: no cover
from _pytest import junitxml
from _pytest.tmpdir import tmpdir

from selenium.webdriver.support import wait

from .webdriver_patches import patch_webdriver  # pragma: no cover
from .splinter_patches import patch_webdriverelement  # pragma: no cover

import logging
LOGGER = logging.getLogger(__name__)


NAME_RE = re.compile(r'[\W]')


def _visit(self, url):
    """Override splinter's visit to avoid unnecessary checks and add wait_until instead."""
    self.__dict__.pop('status_code', None)
    self.driver.get(url)
    self.wait_for_condition(self.visit_condition, timeout=self.visit_condition_timeout)


def _wait_for_condition(self, condition=None, timeout=None, poll_frequency=0.5, ignored_exceptions=None):
    """Wait for given javascript condition."""
    condition = functools.partial(condition or self.visit_condition, self)

    timeout = timeout or self.visit_condition_timeout

    return wait.WebDriverWait(
        self.driver, timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions
    ).until(
        lambda browser: condition()
    )


def _get_status_code(self):
    """Lazy status code get."""
    inst_status_code = self.__dict__.get('status_code')
    if inst_status_code:
        return inst_status_code
    self.connect(self.url)
    return self.status_code


def _set_status_code(self, value):
    """Lazy status code set."""
    self.__dict__['status_code'] = value


def Browser(*args, **kwargs):
    """Emulate splinter's Browser."""
    visit_condition = kwargs.pop('visit_condition')
    visit_condition_timeout = kwargs.pop('visit_condition_timeout')
    browser = splinter.Browser(*args, **kwargs)
    browser.wait_for_condition = functools.partial(_wait_for_condition, browser)
    if hasattr(browser, 'driver'):
        browser.visit_condition = visit_condition
        browser.visit_condition_timeout = visit_condition_timeout
        browser.visit = functools.partial(_visit, browser)
        browser.__class__.status_code = property(_get_status_code, _set_status_code)
    browser.__splinter_browser__ = True
    return browser


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_close_browser():
    """Close browser fixture."""
    return True


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_webdriver(request):
    """Webdriver fixture."""
    return request.config.option.splinter_webdriver


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_remote_url(request):
    """Remote webdriver url.

    :return: URL of remote webdriver.
    """
    return request.config.option.splinter_remote_url


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_socket_timeout(request):
    """Internal Selenium socket timeout (communication between webdriver and the browser).

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_socket_timeout


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_implicit_wait(request):
    """Selenium implicit wait timeout.

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_implicit_wait


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_speed(request):
    """Selenium speed.

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_speed


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_browser_load_condition():
    """The condition that has to be `True` to assume that the page is fully loaded.

    One example is to wait for jQuery, then the condition could be::

        @pytest.fixture
        def splinter_browser_load_condition():

            def condition(browser):
                return browser.evaluate_script('typeof $ === "undefined" || !$.active')

            return condition
    """
    return lambda browser: True


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_browser_load_timeout():
    """The timeout in seconds in which the page is expected to be fully loaded."""
    return 10


@pytest.yield_fixture(scope='session')  # pragma: no cover
def splinter_file_download_dir(request):
    """Browser file download directory."""
    name = request.node.name
    name = NAME_RE.sub("_", name)
    x = request.config._tmpdirhandler.mktemp(name, numbered=True)
    yield x.strpath
    x.remove()


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_download_file_types():
    """Browser file types to download. Comma-separated."""
    return ','.join(mimetypes.types_map.values())


@pytest.fixture(scope='session')
def splinter_firefox_profile_preferences():
    """Firefox profile preferences."""
    return {
        'browser.cache.memory.enable': False,
        'browser.sessionhistory.max_total_viewers': 0,
        'network.http.pipelining': True,
        'network.http.pipelining.maxrequests': 8
    }


@pytest.fixture(scope='session')
def splinter_firefox_profile_directory():
    """Firefox profile directory."""
    return os.path.join(os.path.dirname(__file__), 'profiles', 'firefox')


@pytest.fixture(scope='session')
def splinter_driver_kwargs():
    """Webdriver kwargs."""
    return {}


@pytest.fixture(scope='session')
def splinter_window_size():
    """Browser window size. (width, height)."""
    return (1366, 768)


@pytest.fixture(scope='session')
def splinter_session_scoped_browser(request):
    """Flag to keep single browser per test session."""
    return request.config.option.splinter_session_scoped_browser == 'true'


@pytest.fixture(scope='session')
def splinter_make_screenshot_on_failure(request):
    """Flag to make browser screenshot on test failure."""
    return request.config.option.splinter_make_screenshot_on_failure == 'true'


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_screenshot_dir(request):
    """Browser screenshot directory."""
    return os.path.abspath(request.config.option.splinter_screenshot_dir)


@pytest.fixture(scope='session')
def splinter_webdriver_executable(request):
    """Webdriver executable directory."""
    executable = request.config.option.splinter_webdriver_executable
    return os.path.abspath(executable) if executable else None


@pytest.fixture(scope='session')
def browser_pool(request, splinter_close_browser):
    """Browser 'pool' to emulate session scope but with possibility to recreate browser."""
    pool = {}

    def fin():
        for browser in pool.values():
            try:
                browser.quit()
            except (IOError, OSError):
                pass

    if splinter_close_browser:
        request.addfinalizer(fin)

    return pool


@pytest.fixture(scope='session')
def browser_patches(splinter_selenium_socket_timeout):
    """Browser monkey patches."""
    patch_webdriver(splinter_selenium_socket_timeout)
    patch_webdriverelement()


@pytest.fixture(scope='session')
def session_tmpdir(request):
    """pytest tmpdir which is session-scoped."""
    return tmpdir(request)


@pytest.fixture(scope='session')
def splinter_browser_class(request):
    """Browser class to use for browser instance creation."""
    return Browser


def get_args(driver=None,
             download_dir=None,
             download_ftypes=None,
             firefox_pref=None,
             firefox_prof_dir=None,
             remote_url=None,
             executable=None,
             driver_kwargs=None):
    """Construct arguments to be passed to webdriver on initialization."""
    kwargs = {}

    if driver == 'firefox':
        kwargs['profile_preferences'] = dict({
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir': download_dir,
            'browser.helperApps.neverAsk.saveToDisk': download_ftypes,
            'browser.helperApps.alwaysAsk.force': False,
            'pdfjs.disabled': True,  # disable internal ff pdf viewer to allow auto pdf download
        }, **firefox_pref)
        kwargs['profile'] = firefox_prof_dir
    elif driver == 'remote':
        kwargs['url'] = remote_url
    elif driver in ('phantomjs', 'chrome'):
        if executable:
            kwargs['executable_path'] = executable
    if driver_kwargs:
        kwargs.update(driver_kwargs)

    return kwargs


@pytest.fixture(scope='session')
def browser_instance_getter(
        browser_patches,
        splinter_session_scoped_browser,
        splinter_browser_load_condition,
        splinter_browser_load_timeout,
        splinter_download_file_types,
        splinter_driver_kwargs,
        splinter_file_download_dir,
        splinter_firefox_profile_preferences,
        splinter_firefox_profile_directory,
        splinter_make_screenshot_on_failure,
        splinter_remote_url,
        splinter_screenshot_dir,
        splinter_selenium_implicit_wait,
        splinter_selenium_socket_timeout,
        splinter_selenium_speed,
        splinter_webdriver,
        splinter_webdriver_executable,
        splinter_window_size,
        splinter_browser_class,
        session_tmpdir,
        browser_pool,
):
    """Splinter browser instance getter. To be used for getting of plugin.Browser's instances.

    :return: function(parent). Each time this function will return new instance of plugin.Browser class.
    """
    def get_browser():
        kwargs = get_args(driver=splinter_webdriver,
                          download_dir=splinter_file_download_dir,
                          download_ftypes=splinter_download_file_types,
                          firefox_pref=splinter_firefox_profile_preferences,
                          firefox_prof_dir=splinter_firefox_profile_directory,
                          remote_url=splinter_remote_url,
                          executable=splinter_webdriver_executable,
                          driver_kwargs=splinter_driver_kwargs)
        return splinter_browser_class(
            splinter_webdriver, visit_condition=splinter_browser_load_condition,
            visit_condition_timeout=splinter_browser_load_timeout,
            wait_time=splinter_selenium_implicit_wait, **kwargs
        )

    def prepare_browser(request, parent):
        browser_key = id(parent)
        browser = browser_pool.get(browser_key)
        if not splinter_session_scoped_browser:
            browser = get_browser()
            if splinter_close_browser:
                request.addfinalizer(browser.quit)
        elif not browser:
            browser = browser_pool[browser_key] = get_browser()
        try:
            if splinter_webdriver not in browser.driver_name.lower():
                raise IOError('webdriver does not match')
            if hasattr(browser, 'driver'):
                browser.driver.implicitly_wait(splinter_selenium_implicit_wait)
                browser.driver.set_speed(splinter_selenium_speed)
                if splinter_window_size:
                    browser.driver.set_window_size(*splinter_window_size)
            browser.cookies.delete()
            if hasattr(browser, 'driver'):
                browser.visit_condition = splinter_browser_load_condition
                browser.visit_condition_timeout = splinter_browser_load_timeout
                browser.visit('about:blank')
        except (IOError, HTTPException):
            # we lost browser, try to restore the justice
            try:
                browser.quit()
            except Exception:  # NOQA
                pass
            browser = browser_pool[browser_key] = get_browser()
            prepare_browser(request, parent)

        return browser

    return prepare_browser


@pytest.yield_fixture(autouse=True)
def browser_screenshot(request, splinter_screenshot_dir):
    """Make browser screenshot on test failure."""
    yield
    for name, value in request._funcargs.items():
        if hasattr(value, '__splinter_browser__'):
            browser = value
            if splinter_make_screenshot_on_failure and request.node.splinter_failure:
                slaveoutput = getattr(request.config, 'slaveoutput', None)
                names = junitxml.mangle_testnames(request.node.nodeid.split("::"))
                classname = '.'.join(names[:-1])
                screenshot_dir = os.path.join(splinter_screenshot_dir, classname)
                screenshot_file_name = '{0}-{1}.png'.format(
                    names[-1][:128 - len(name) - 5], name)
                if not slaveoutput:
                    if not os.path.exists(screenshot_dir):
                        os.makedirs(screenshot_dir)
                else:
                    screenshot_dir = session_tmpdir.mkdir('screenshots').strpath
                screenshot_path = os.path.join(screenshot_dir, screenshot_file_name)
                LOGGER.info('Saving screenshot to %s', screenshot_path)
                try:
                    browser.driver.save_screenshot(screenshot_path)
                    with open(screenshot_path) as fd:
                        if slaveoutput is not None:
                            slaveoutput.setdefault('screenshots', []).append({
                                'class_name': classname,
                                'file_name': screenshot_file_name,
                                'content': fd.read()
                            })
                except Exception as e:  # NOQA
                    request.config.warn('SPL504', "Could not save screenshot: {0}".format(e))


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    """Assign the report to the item for futher usage."""
    rep = __multicall__.execute()
    if rep.outcome != 'passed':
        item.splinter_failure = rep
    else:
        item.splinter_failure = None
    return rep


@pytest.fixture
def browser(request, browser_instance_getter):
    """Browser fixture."""
    return browser_instance_getter(request, browser)


@pytest.fixture(scope='session')
def session_browser(request, browser_instance_getter):
    """Session scoped browser fixture."""
    return browser_instance_getter(request, session_browser)


class SplinterXdistPlugin(object):

    """Plugin class to defer pytest-xdist hook handler."""

    def pytest_testnodedown(self, node, error):
        """Copy screenshots back from remote nodes to have them on the master."""
        config_screenshot_dir = splinter_screenshot_dir(node)
        for screenshot in getattr(node, 'slaveoutput', {}).get('screenshots', []):
            screenshot_dir = os.path.join(config_screenshot_dir, screenshot['class_name'])
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            with open(os.path.join(screenshot_dir, screenshot['file_name']), 'w') as fd:
                fd.write(screenshot['content'])


def pytest_configure(config):
    """Register pytest-splinter's deferred plugin."""
    if config.pluginmanager.getplugin('xdist'):
        config.pluginmanager.register(SplinterXdistPlugin())


def pytest_addoption(parser):  # pragma: no cover
    """Pytest hook to add custom command line option(s)."""
    group = parser.getgroup("splinter", "splinter integration for browser testing")
    group.addoption(
        "--splinter-webdriver",
        help="pytest-splinter webdriver", type="choice", choices=list(splinter.browser._DRIVERS.keys()),
        dest='splinter_webdriver', metavar="DRIVER", default='firefox')
    group.addoption(
        "--splinter-remote-url",
        help="pytest-splinter remote webdriver url ", metavar="URL", dest='splinter_remote_url', default=None)
    group.addoption(
        "--splinter-implicit-wait",
        help="pytest-splinter selenium implicit wait, seconds", type="int",
        dest='splinter_webdriver_implicit_wait', metavar="SECONDS", default=5)
    group.addoption(
        "--splinter-speed",
        help="pytest-splinter selenium speed, seconds", type="int",
        dest='splinter_webdriver_speed', metavar="SECONDS", default=0)
    group.addoption(
        "--splinter-socket-timeout",
        help="pytest-splinter socket timeout, seconds", type="int",
        dest='splinter_webdriver_socket_timeout', metavar="SECONDS", default=120)
    group.addoption(
        "--splinter-session-scoped-browser",
        help="pytest-splinter should use a single browser instance per test session. Defaults to true.", action="store",
        dest='splinter_session_scoped_browser', metavar="false|true", type="choice", choices=['false', 'true'],
        default='true')
    group.addoption(
        "--splinter-make-screenshot-on-failure",
        help="pytest-splinter should take browser screenshots on test failure. Defaults to true.", action="store",
        dest='splinter_make_screenshot_on_failure', metavar="false|true", type="choice", choices=['false', 'true'],
        default='true')
    group.addoption(
        "--splinter-screenshot-dir",
        help="pytest-splinter browser screenshot directory. Defaults to the current directory.", action="store",
        dest='splinter_screenshot_dir', metavar="DIR", default='.')
    group.addoption(
        "--splinter-webdriver-executable",
        help="pytest-splinter webdrive executable path. Defaults to unspecified in which case it is taken from PATH",
        action="store",
        dest='splinter_webdriver_executable', metavar="DIR", default='')
