"""Browser screenshot tests."""


def test_browser_screenshot_normal(testdir, mocked_browser):
    """Test making screenshots on test failure if the commandline option is passed.

    Normal test run.
    """
    testdir.inline_runsource("""
        def test_screenshot(browser):
            assert False
    """, "-vl", "--splinter-session-scoped-browser=false")

    assert testdir.tmpdir.join('test_browser_screenshot_normal', 'test_screenshot.png').isfile()


def test_browser_screenshot_xdist(testdir, mocked_browser):
    """Test making screenshots on test failure if the commandline option is passed.

    Distributed test run.
    """
    testdir.inline_runsource("""
        def test_screenshot(browser):
            assert False
    """, "-vl", "-n1")

    assert testdir.tmpdir.join('test_browser_screenshot_xdist', 'test_screenshot.png').isfile()
