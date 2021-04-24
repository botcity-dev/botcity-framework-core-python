from functools import wraps
import platform
import subprocess

from .base import SingleState


def is_retina():
    """
    Check whether or not the system is running in "retina" display mode.

    Returns:
    (bool)
    """
    if platform.system() == 'Darwin':
        check = subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check == 0:
            return True
    return False


def ensure_state(func):
    """
    Decorator to ensure that a State instance is being provided.
    If no State instance is provided it uses the singleton SingleState.

    Args:
        func (callable): The function to be wrapped

    Returns:
        wrapper (callable): The decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'stage' not in kwargs:
            kwargs['state'] = SingleState()
        return func(*args, **kwargs)
    return wrapper


def only_if_element(func):
    """
    Decorator which raises if element is None.

    Args:
        func (callable): The function to be wrapped

    Returns:
        wrapper (callable): The decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        state = kwargs.get('state', SingleState())
        if state.element is None:
            raise ValueError(f'Element not available. Cannot invoke {func.__name__}.')
        return func(*args, **kwargs)
    return wrapper
