Changelog
=========

1.2.8
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
