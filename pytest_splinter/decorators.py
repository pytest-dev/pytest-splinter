"""Decorators."""
import inspect
from functools import wraps


def with_fixtures(func):
    """A decorator that allows to call a function with the with_fixtures as parameters.

    :returns: Function that takes request parameter and optional keyword arguments to override fixtures.
    """
    @wraps(func)
    def decorate(request, **kwargs):
        call_args = {}
        for arg in inspect.getargspec(func).args:
            if arg in kwargs:
                call_args[arg] = kwargs[arg]
            else:
                call_args[arg] = request.getfuncargvalue(arg)
        return func(**call_args)
    return decorate
