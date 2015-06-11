Changelog
=========

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
