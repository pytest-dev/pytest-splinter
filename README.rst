Splinter plugin for the py.test runner
=========================================================

.. image:: https://api.travis-ci.org/paylogic/pytest-splinter.png
   :target: https://travis-ci.org/paylogic/pytest-splinter
.. image:: https://pypip.in/v/pytest-splinter/badge.png
   :target: https://crate.io/packages/pytest-splinter/
.. image:: https://coveralls.io/repos/paylogic/pytest-splinter/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/pytest-splinter


Install pytest-splinter
===========================

::

    pip install pytest-splinter


Features
========

The plugin provides a set of fixtures to use `splinter <http://splinter.cobrateam.info>`_
for browser testing with `pytest <http://pytest.org>`_


Fixtures
========

* browser
    Get the splinter's Browser. Fixture is underneath session scoped, so browser process is started
    once per test session.

* browser_instance_getter
    Function to create an instance of the browser. This fixture is required only if you need to have
    multiple instances of the Browser in a single test at the same time. Example of usage:

.. code-block:: python

    @pytest.fixture
    def admin_browser(browser_instance_getter):
        """Admin browser fixture."""
        # browser_instance_getter function receives single argument - parent fixture
        # in our case it's admin_browser
        return browser_instance_getter(admin_browser)

    def test_2_browsers(browser, admin_browser):
        """Test using 2 browsers at the same time."""
        browser.visit('http://google.com')
        admin_browser.visit('http://admin.example.com')

* splinter_selenium_implicit_wait
    Implicit wait timeout to be passed to Selenium webdriver.
    Fixture gets the value from the command-line option splinter-implicit-wait (see below)

* splinter_selenium_speed
    Speed for Selenium, if not 0 then it will sleep between each selenium command.
    Useful for debugging/demonstration.
    Fixture gets the value from the command-line option splinter-speed (see below)

* splinter_selenium_socket_timeout
    Socket timeout for communication between the webdriver and the browser.
    Fixture gets the value from the command-line option splinter-socket-timeout (see below)

* splinter_webdriver
    Splinter's webdriver name to use. Fixture gets the value from the command-line option
    splinter-webdriver (see below)

* splinter_remote_url
    Splinter's webdriver remote url to use (optional). Fixture gets the value from the command-line option
    splinter-remote-url (see below). Will be used only if selected webdriver name is 'remote'.

* splinter_session_scoped_browser
    pytest-splinter should use single browser instance per test session.
    Fixture gets the value from the command-line option splinter-session-scoped-browser (see below)

* splinter_file_download_dir
    Directory, to which browser will automatically download the files it
    will experience during browsing. For example when you click on some download link.
    By default it's a temporary directory. Automatic downloading of files is only supported for firefox driver
    at the moment.

* splinter_download_file_types
    Comma-separated list of content types to automatically download.
    By default it's the all known system mime types (via mimetypes standard library).

* splinter_browser_load_condition
    Browser load condition, python function which should return True.
    If function returns False, it will be run several times, until timeout below reached.

* splinter_browser_load_timeout
    Browser load condition timeout in seconds, after this timeout the exception
    WaitUntilTimeout will be raised.

* splinter_firefox_profile_preferences
    Firefox profile preferences, a dictionary which is passed to selenium
    webdriver's profile_preferences

* splinter_driver_kwargs
    Webdriver keyword arguments, a dictionary which is passed to selenium
    webdriver's constructor (after applying firefox preferences)

* splinter_window_size
    Size of the browser window on browser initialization. Tuple in form (<width>, <height>). Default is (1366, 768)


Command-line options
====================

* `--splinter-implicit-wait`
    Selenium webdriver implicit wait. Seconds (default: 1).

* `--splinter-speed`
    selenium webdriver speed (from command to command). Seconds (default: 0).

* `--splinter-socket-timeout`
    Selenium webdriver socket timeout for for communication between the webdriver and the browser.
    Seconds (default: 120).

* `--splinter-webdriver`
    Webdriver name to use. (default: firefox). Options:

    *  firefox
    *  remote
    *  chrome
    *  phantomjs

    For more details, refer to splinter and selenium documentation.

* `--splinter-remote-url`
    Webdriver remote url to use. (default: None). Will be used only if selected webdriver name is 'remote'.

    For more details, refer to splinter and selenium documentation.

* `--splinter-session-scoped-browser`
    pytest-splinter should use single browser instance per test session. (set by default).


Browser fixture
===============

As mentioned above, browser is a fixture made by creating splinter's Browser object, but with some overrides.

*  visit
    Added possibility to wait for condition on each browser visit by having a fixture.

*  wait_for_condition
    Method copying selenium's wait_for_condition, with difference that condition is in python,
    so there you can do whatever you want, and not only execute javascript via browser.evaluate_script.

*  `status_code <http://splinter.cobrateam.info/docs/http-status-code-and-exception.html>`_
    This functionality is removed, so not available. Splinter implements this using additional request from python side,
    which is in general performance-wise not a good idea. Also normally when you interact with the browser as a user,
    you don't need the status code of the page.

Several browsers for your test
==============================

You can have several browsers in one test.

.. code-block:: python

    import pytest

    @pytest.fixture 
    def admin_browser(browser_instance_getter):
        return browser_instance_getter(admin_browser)
        
    def test_with_several_browsers(browser, admin_browser):
        browser.visit('http://example.com')
        admin_browser.visit('about:blank')
        assert browser.url == 'http://example.com'


Python3 support
===============

Python3 is supported, check if you have recent version of splinter as it was added recently.


Example
=======

test_your_test.py:

.. code-block:: python

    def test_some_browser_stuff(browser):
        """Test using real browser."""
        url = "http://www.google.com"
        browser.visit(url)
        browser.fill('q', 'splinter - python acceptance testing for web applications')
        # Find and click the 'search' button
        button = browser.find_by_name('btnK')
        # Interact with elements
        button.click()
        assert browser.is_text_present('splinter.cobrateam.info'), 'splinter.cobrateam.info wasn't found... We need to'
        ' improve our SEO techniques'


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/pytest-splinter>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License <https://github.com/paylogic/pytest-splinter/blob/master/LICENSE.txt>`_


© 2014 Paylogic International.
