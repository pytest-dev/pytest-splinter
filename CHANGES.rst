Changelog
=========

1.7.4
-----

- use tmpdir_factory to get session scoped tmpdir (RonnyPfannschmidt, bubenkoff)


1.7.3
-----

- fixed Firefox freezing when opening a missing codec extension (olegpidsadnyi)


1.7.2
-----

- fixed taking a screenshot with pytest>=2.9.0 (olegpidsadnyi)


1.7.1
-----

- pytest warnings fixed (firebirdberlin)
- remove firefox firstrun script (aaugustin, bubenkoff)

1.7.0
-----

- add possibility to clean cookies on given domains during the browser cleanup, document cookies cleanup (bubenkoff)

1.6.6
-----

- screenshot encoding made flexible (bubenkoff)

1.6.2
-----

- pass timeout to restored connection (bubenkoff)

1.6.0
-----

- added html screenshot (bubenkoff, blueyed)

1.5.3
-----

- remote webdriver fixes (bubenkoff)

1.5.2
-----

- respect splinter_make_screenshot_on_failure (bubenkoff)

1.5.1
-----

- use native selenium socket timeout feature (pelme)

1.5.0
-----

- pytest tmpdir_factory support (bubenkoff)
- depend on splinter 0.7.3, remove the previous status_code monkey patch (pelme)
- add option `--splinter-wait-time` to specify splinter explicit wait timeout (pelme)

1.4.6
-----

- ensure base tempdir exists (bubenkoff)


1.4.0
-----

- introduce splinter_browser_class fixture (bubenkoff, ecesena)


1.3.8
-----

- correctly handle zope.testbrowser splinter driver (bubenkoff)


1.3.7
-----

- pass `splinter_selenium_implicit_wait` as `wait_time` to splinter Browser (lrowe)


1.3.6
-----

- properly respect webdriver executable command line option (bubenkoff, bh)


1.3.5
-----

- add option --splinter-webdriver-executable for phantomjs and chrome (sureshvv)


1.3.4
-----

- make ``browser_instance_getter`` session scoped, add ``session_browser`` fixture (bubenkoff, sureshvv)


1.3.3
-----

- make ``mouse_over`` comparible with more use-cases (bubenkoff)


1.3.1
-----

- properly handle driver switch during the test run (bubenkoff)
- respect splinter_session_scoped_browser fixture (bubenkoff)


1.2.10
------

- handle exceptions during screenshot saving (blueyed, bubenkoff)
- documentation improvements (blueyed)


1.2.9
-----

- status_code is back in a lazy way (bubenkoff)


1.2.7
-----

- Fix automatic download of pdf content type (bubenkoff)


1.2.4
-----

- fix failing the test run if pytest-xdist is not installed, as it's completely optional dependency (bubenkoff, slafs)


1.2.3
-----

- improve exception handing when preparing the browser instance (bubenkoff)
- require pytest (bubenkoff)


1.2.0
-----

- automatic screenshot capture on test failure (bubenkoff)
- improvements to the browser preparation procedure (bubenkoff)
- boolean config options made more clear (bubenkoff)


1.1.1
-----

- restore browser parameters on each test run instead of once for browser start (bubenkoff)


1.1.0
-----

- added possibility to have multiple browser instances for single test (amakhnach, bubenkoff)


1.0.4
-----

- Fixed browser fixture to support splinter_browser_load_condition and splinter_browser_load_timeout by default. (markon)


1.0.3
-----

- unicode fixes to setup.py (bubenkoff, valberg)


1.0.2
-----

- wait_for_condition now receives pytest_bdd.plugin.Browser object, not selenium webdriver one (bubenkoff)


1.0.1
-----

- Refactoring and cleanup (bubenkoff)


1.0.0
-----

- Initial public release
