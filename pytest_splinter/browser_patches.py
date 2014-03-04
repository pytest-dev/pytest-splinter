"""Browser patches."""
import time  # pragma: no cover


def wait_until(browser, condition, timeout=10):
    """Wait until the condition becomes false or the timeout happens.

    :param condition: a callable that takes no parameters, returns a boolean.
    :param timeout: the timout time

    """
    max_time = time.time() + timeout

    while not condition(browser):
        if time.time() > max_time:
            raise WaitUntilTimeout()

        time.sleep(0.1)

    return True


class WaitUntilTimeout(Exception):  # pragma: no cover
    """Thrown when the timeout happened during waiting for a condition."""
