"""Splinter plugin for pytest.

Provides easy interface for the browser from your tests providing the `browser` fixture
which is an object of splinter Browser class.
"""
import codecs
import functools  # pragma: no cover
import warnings

try:
    from httplib import HTTPException
except ImportError:
    from http.client import HTTPException
import logging
import mimetypes  # pragma: no cover
import os.path
import re

import pytest  # pragma: no cover
import splinter  # pragma: no cover
from _pytest import junitxml

from urllib3.exceptions import MaxRetryError

from selenium.webdriver.support import wait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import WebDriverException

from .webdriver_patches import patch_webdriver  # pragma: no cover
from .splinter_patches import patch_webdriverelement  # pragma: no cover


LOGGER = logging.getLogger(__name__)


NAME_RE = re.compile(r'[\W]')


def _visit(self, old_visit, url):
    """Override splinter's visit to avoid unnecessary checks and add wait_until instead."""
    old_visit(url)
    self.wait_for_condition(self.visit_condition, timeout=self.visit_condition_timeout)


def _wait_for_condition(self, condition=None, timeout=None, poll_frequency=0.5, ignored_exceptions=None):
    """Wait for given javascript condition."""
    condition = functools.partial(condition or self.visit_condition, self)

    timeout = timeout or self.wait_time

    return wait.WebDriverWait(
        self.driver, timeout, poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions
    ).until(
        lambda browser: condition()
    )


def _screenshot_extraline(screenshot_png_file_name, screenshot_html_file_name):
    return """
===========================
pytest-splinter screenshots
===========================
png:  %s
html: %s
""" % (screenshot_png_file_name, screenshot_html_file_name)


def Browser(*args, **kwargs):
    """Emulate splinter's Browser."""
    visit_condition = kwargs.pop('visit_condition')
    visit_condition_timeout = kwargs.pop('visit_condition_timeout')
    browser = splinter.Browser(*args, **kwargs)
    browser.switch_to = browser.driver.switch_to
    browser.wait_for_condition = functools.partial(_wait_for_condition, browser)
    if hasattr(browser, 'driver'):
        browser.visit_condition = visit_condition
        browser.visit_condition_timeout = visit_condition_timeout
        browser.visit = functools.partial(_visit, browser, browser.visit)
    browser.__splinter_browser__ = True
    return browser


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_close_browser():
    """Close browser fixture."""
    return True


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_webdriver(request):
    """Webdriver fixture."""
    return request.config.option.splinter_webdriver or 'firefox'


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_remote_url(request):
    """Remote webdriver url.

    :return: URL of remote webdriver.
    """
    return request.config.option.splinter_remote_url


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_socket_timeout(request):
    """Return internal Selenium socket timeout (communication between webdriver and the browser).

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_socket_timeout


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_implicit_wait(request):
    """Return Selenium implicit wait timeout.

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_implicit_wait


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_wait_time(request):
    """Splinter explicit wait timeout.

    :return: Seconds.
    """
    return request.config.option.splinter_wait_time or 5


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_selenium_speed(request):
    """Selenium speed.

    :return: Seconds.
    """
    return request.config.option.splinter_webdriver_speed


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_browser_load_condition():
    """Return the condition that has to be `True` to assume that the page is fully loaded.

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
    """Return the timeout in seconds in which the page is expected to be fully loaded."""
    return 10


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_file_download_dir(session_tmpdir):
    """Browser file download directory."""
    return session_tmpdir.ensure('splinter', 'download', dir=True).strpath


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
        'network.http.pipelining.maxrequests': 8,
        'browser.startup.page': 0,
        'browser.startup.homepage': 'about:blank',
        'startup.homepage_welcome_url': 'about:blank',
        'startup.homepage_welcome_url.additional': 'about:blank',
        'browser.startup.homepage_override.mstone': 'ignore',
        'toolkit.telemetry.reportingpolicy.firstRun': False,
        'datareporting.healthreport.service.firstRun': False,
        'browser.cache.disk.smart_size.first_run': False,
        'media.gmp-gmpopenh264.enabled': False,  # Firefox hangs when the file is not found
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
def splinter_headless(request):
    """Flag to start Chrome in headless mode.

    http://splinter.readthedocs.io/en/latest/drivers/chrome.html#using-headless-option-for-chrome
    """
    return request.config.option.splinter_headless == 'true'


@pytest.fixture(scope='session')  # pragma: no cover
def splinter_screenshot_encoding(request):
    """Browser screenshot html encoding."""
    return 'utf-8'


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
            except Exception:  # NOQA
                pass

    if splinter_close_browser:
        request.addfinalizer(fin)

    return pool


@pytest.fixture(scope='session')
def browser_patches():
    """Browser monkey patches."""
    patch_webdriver()
    patch_webdriverelement()


@pytest.fixture(scope='session')
def session_tmpdir(tmpdir_factory):
    """pytest tmpdir which is session-scoped."""
    return tmpdir_factory.mktemp('pytest-splinter')


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
             headless=False,
             driver_kwargs=None):
    """Construct arguments to be passed to webdriver on initialization."""
    kwargs = {}

    firefox_profile_preferences = dict({
        'browser.download.folderList': 2,
        'browser.download.manager.showWhenStarting': False,
        'browser.download.dir': download_dir,
        'browser.helperApps.neverAsk.saveToDisk': download_ftypes,
        'browser.helperApps.alwaysAsk.force': False,
        'pdfjs.disabled': True,  # disable internal ff pdf viewer to allow auto pdf download
    }, **firefox_pref or {})

    if driver == 'firefox':
        kwargs['profile_preferences'] = firefox_profile_preferences
        kwargs['profile'] = firefox_prof_dir
    elif driver == 'remote':
        if remote_url:
            kwargs['url'] = remote_url
        kwargs['keep_alive'] = True
        profile = FirefoxProfile(firefox_prof_dir)
        for key, value in firefox_profile_preferences.items():
            profile.set_preference(key, value)
        kwargs['firefox_profile'] = profile.encoded

        # remote geckodriver does not support the firefox_profile desired
        # capatibility. Instead `moz:firefoxOptions` should be used:
        # https://github.com/mozilla/geckodriver#firefox-capabilities
        kwargs['moz:firefoxOptions'] = driver_kwargs.get('moz:firefoxOptions', {})
        kwargs['moz:firefoxOptions']['profile'] = profile.encoded
    elif driver in ('chrome',):
        if executable:
            kwargs['executable_path'] = executable

        if headless:
            kwargs["headless"] = headless

    if driver_kwargs:
        kwargs.update(driver_kwargs)
    return kwargs


@pytest.fixture(scope='session')
def splinter_screenshot_getter_png():
    """Screenshot getter function: png."""
    def getter(browser, path):
        browser.driver.save_screenshot(path)
    return getter


@pytest.fixture(scope='session')
def splinter_screenshot_getter_html(splinter_screenshot_encoding):
    """Screenshot getter function: html."""
    def getter(browser, path):
        with codecs.open(path, 'w', encoding=splinter_screenshot_encoding) as fd:
            fd.write(browser.html)
    return getter


@pytest.fixture(scope='session')
def splinter_clean_cookies_urls():
    """List of urls to clean cookies on their domains."""
    return []


def _take_screenshot(
        request,
        browser_instance,
        fixture_name,
        session_tmpdir,
        splinter_screenshot_dir,
        splinter_screenshot_getter_html,
        splinter_screenshot_getter_png,
        splinter_screenshot_encoding,
):
    """Capture a screenshot as .png and .html.

    Invoked from session and function browser fixtures.
    """
    slaveoutput = getattr(request.config, 'slaveoutput', None)
    try:
        names = junitxml.mangle_testnames(request.node.nodeid.split("::"))
    except AttributeError:
        # pytest>=2.9.0
        names = junitxml.mangle_test_address(request.node.nodeid)

    classname = '.'.join(names[:-1])
    screenshot_dir = os.path.join(splinter_screenshot_dir, classname)
    screenshot_file_name_format = '{0}.{{format}}'.format(
        '{0}-{1}'.format(names[-1][:128 - len(fixture_name) - 5], fixture_name).replace(os.path.sep, '-')
    )
    screenshot_file_name = screenshot_file_name_format.format(format='png')
    screenshot_html_file_name = screenshot_file_name_format.format(format='html')
    if not slaveoutput:
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
    else:
        screenshot_dir = session_tmpdir.ensure('screenshots', dir=True).strpath
    screenshot_png_path = os.path.join(screenshot_dir, screenshot_file_name)
    screenshot_html_path = os.path.join(screenshot_dir, screenshot_html_file_name)
    LOGGER.info('Saving screenshot to %s', screenshot_dir)
    try:
        splinter_screenshot_getter_html(browser_instance, screenshot_html_path)
        splinter_screenshot_getter_png(browser_instance, screenshot_png_path)
        if request.node.splinter_failure.longrepr:
            reprtraceback = request.node.splinter_failure.longrepr.reprtraceback
            reprtraceback.extraline = _screenshot_extraline(screenshot_png_path, screenshot_html_path)
        if slaveoutput is not None:
            with codecs.open(screenshot_html_path, encoding=splinter_screenshot_encoding) as html_fd:
                with open(screenshot_png_path, 'rb') as fd:
                    slaveoutput.setdefault('screenshots', []).append({
                        'class_name': classname,
                        'files': [
                            {
                                'file_name': screenshot_file_name,
                                'content': fd.read(),
                            },
                            {
                                'file_name': screenshot_html_file_name,
                                'content': html_fd.read(),
                                'encoding': splinter_screenshot_encoding,
                            }]
                    })
    except Exception as e:  # NOQA
        warnings.warn(pytest.PytestWarning("Could not save screenshot: {0}".format(e)))


@pytest.yield_fixture(autouse=True)
def _browser_screenshot_session(
        request,
        session_tmpdir,
        splinter_session_scoped_browser,
        splinter_screenshot_dir,
        splinter_make_screenshot_on_failure,
        splinter_screenshot_getter_html,
        splinter_screenshot_getter_png,
        splinter_screenshot_encoding,
):
    """Make browser screenshot on test failure."""
    yield

    # Screenshot for function scoped browsers is handled in browser_instance_getter
    if not splinter_session_scoped_browser:
        return

    fixture_values = (
        # pytest 3
        getattr(request, '_fixture_values', {}) or
        # pytest 2
        getattr(request, '_funcargs', {})
    )

    for name, value in fixture_values.items():
        should_take_screenshot = (
            hasattr(value, '__splinter_browser__') and
            splinter_make_screenshot_on_failure and
            getattr(request.node, 'splinter_failure', True)
        )

        if should_take_screenshot:
            _take_screenshot(
                request=request,
                fixture_name=name,
                session_tmpdir=session_tmpdir,
                browser_instance=value,
                splinter_screenshot_dir=splinter_screenshot_dir,
                splinter_screenshot_getter_html=splinter_screenshot_getter_html,
                splinter_screenshot_getter_png=splinter_screenshot_getter_png,
                splinter_screenshot_encoding=splinter_screenshot_encoding,
            )


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
        splinter_wait_time,
        splinter_selenium_socket_timeout,
        splinter_selenium_speed,
        splinter_webdriver_executable,
        splinter_window_size,
        splinter_browser_class,
        splinter_clean_cookies_urls,
        splinter_screenshot_getter_html,
        splinter_screenshot_getter_png,
        splinter_screenshot_encoding,
        splinter_headless,
        session_tmpdir,
        browser_pool,
):
    """Splinter browser instance getter. To be used for getting of plugin.Browser's instances.

    :return: function(parent). Each time this function will return new instance of plugin.Browser class.
    """
    def get_browser(splinter_webdriver, retry_count=3):
        kwargs = get_args(driver=splinter_webdriver,
                          download_dir=splinter_file_download_dir,
                          download_ftypes=splinter_download_file_types,
                          firefox_pref=splinter_firefox_profile_preferences,
                          firefox_prof_dir=splinter_firefox_profile_directory,
                          remote_url=splinter_remote_url,
                          executable=splinter_webdriver_executable,
                          headless=splinter_headless,
                          driver_kwargs=splinter_driver_kwargs)
        try:
            return splinter_browser_class(
                splinter_webdriver, visit_condition=splinter_browser_load_condition,
                visit_condition_timeout=splinter_browser_load_timeout,
                wait_time=splinter_wait_time, **kwargs
            )
        except Exception:  # NOQA
            if retry_count > 1:
                return get_browser(splinter_webdriver, retry_count - 1)
            else:
                raise

    def prepare_browser(request, parent, retry_count=3):
        splinter_webdriver = request.getfixturevalue('splinter_webdriver')
        splinter_session_scoped_browser = request.getfixturevalue('splinter_session_scoped_browser')
        splinter_close_browser = request.getfixturevalue('splinter_close_browser')
        browser_key = id(parent)
        browser = browser_pool.get(browser_key)
        if not splinter_session_scoped_browser:
            browser = get_browser(splinter_webdriver)
            if splinter_close_browser:
                request.addfinalizer(browser.quit)
        elif not browser:
            browser = browser_pool[browser_key] = get_browser(splinter_webdriver)

        if request.scope == 'function':
            def _take_screenshot_on_failure():
                if splinter_make_screenshot_on_failure and getattr(request.node, 'splinter_failure', True):
                    _take_screenshot(
                        request=request,
                        fixture_name=parent.__name__,
                        session_tmpdir=session_tmpdir,
                        browser_instance=browser,
                        splinter_screenshot_dir=splinter_screenshot_dir,
                        splinter_screenshot_getter_html=splinter_screenshot_getter_html,
                        splinter_screenshot_getter_png=splinter_screenshot_getter_png,
                        splinter_screenshot_encoding=splinter_screenshot_encoding,
                    )
            request.addfinalizer(_take_screenshot_on_failure)

        try:
            if splinter_webdriver not in browser.driver_name.lower():
                raise IOError('webdriver does not match')
            if hasattr(browser, 'driver'):
                browser.driver.implicitly_wait(splinter_selenium_implicit_wait)
                browser.driver.set_speed(splinter_selenium_speed)
                browser.driver.command_executor.set_timeout(splinter_selenium_socket_timeout)
                browser.driver.command_executor._conn.timeout = splinter_selenium_socket_timeout
                if splinter_window_size and splinter_webdriver != "chrome":
                    # Chrome cannot resize the window
                    # https://github.com/SeleniumHQ/selenium/issues/3508
                    browser.driver.set_window_size(*splinter_window_size)
            try:
                browser.cookies.delete()
            except (IOError, HTTPException, WebDriverException):
                LOGGER.warning('Error cleaning browser cookies', exc_info=True)
            for url in splinter_clean_cookies_urls:
                browser.visit(url)
                browser.cookies.delete()
            if hasattr(browser, 'driver'):
                browser.visit_condition = splinter_browser_load_condition
                browser.visit_condition_timeout = splinter_browser_load_timeout
                browser.visit('about:blank')
        except (IOError, HTTPException, WebDriverException, MaxRetryError):
            # we lost browser, try to restore the justice
            try:
                browser.quit()
            except Exception:  # NOQA
                pass
            LOGGER.warning('Error preparing the browser', exc_info=True)
            if retry_count < 1:
                raise
            else:
                browser = browser_pool[browser_key] = get_browser(splinter_webdriver)
                prepare_browser(request, parent, retry_count - 1)
        return browser

    return prepare_browser


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Assign the report to the item for futher usage."""
    outcome = yield
    rep = outcome.get_result()
    if rep.outcome == 'failed':
        item.splinter_failure = rep
    else:
        item.splinter_failure = None


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

    def __init__(self, screenshot_dir):
        """Initialize the SplinterXdistPlugin with the required configuration."""
        self.screenshot_dir = screenshot_dir

    def pytest_testnodedown(self, node, error):
        """Copy screenshots back from remote nodes to have them on the master."""
        for screenshot in getattr(node, 'slaveoutput', {}).get('screenshots', []):
            screenshot_dir = os.path.join(self.screenshot_dir, screenshot['class_name'])
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            for fil in screenshot['files']:
                encoding = fil.get('encoding')
                with codecs.open(os.path.join(screenshot_dir, fil['file_name']), 'wb',
                                 **dict(encoding=encoding) if encoding else {}) as fd:
                    fd.write(fil['content'])


def pytest_configure(config):
    """Register pytest-splinter's deferred plugin."""
    if config.pluginmanager.getplugin('xdist'):
        screenshot_dir = os.path.abspath(config.option.splinter_screenshot_dir)
        config.pluginmanager.register(SplinterXdistPlugin(screenshot_dir=screenshot_dir))


def pytest_addoption(parser):  # pragma: no cover
    """Pytest hook to add custom command line option(s)."""
    group = parser.getgroup("splinter", "splinter integration for browser testing")
    group.addoption(
        "--splinter-webdriver",
        help="pytest-splinter webdriver", type="choice", choices=list(splinter.browser._DRIVERS.keys()),
        dest='splinter_webdriver', metavar="DRIVER", default=None)
    group.addoption(
        "--splinter-remote-url",
        help="pytest-splinter remote webdriver url ", metavar="URL", dest='splinter_remote_url', default=None)
    group.addoption(
        "--splinter-wait-time",
        help="splinter explicit wait, seconds", type="int",
        dest='splinter_wait_time', metavar="SECONDS", default=None)
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
    group.addoption(
        "--splinter-headless",
        help="Run the browser in headless mode. Defaults to false. Only applies to Chrome.", action="store",
        dest='splinter_headless', metavar="false|true", type="choice", choices=['false', 'true'],
        default='false')
