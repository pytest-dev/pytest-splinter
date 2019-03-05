from pluggy import HookspecMarker

hookspec = HookspecMarker("pytest")


@hookspec(firstresult=True)
def pytest_splinter_screenshot_dir(config):
    """Return the name of the directory to store test screenshots in."""
    pass
