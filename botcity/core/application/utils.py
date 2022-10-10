import enum
import platform
from functools import wraps


class Backend(str, enum.Enum):
    """
    Supported accessibility technologies.
    [See more details about the Backend types\
    ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/#backend).

    Attributes:
        WIN_32 (str): 'win32' backend
        UIA (str): 'uia' backend
    """
    WIN_32 = "win32"
    UIA = "uia"


def if_windows_os(func):
    """
    Decorator which raises if the OS is not Windows.

    Args:
        func (callable): The function to be wrapped

    Returns:
        wrapper (callable): The decorated function
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if platform.system() == "Windows":
            return func(self, *args, **kwargs)
        raise ValueError(
                f'You can connect to an application on Windows OS only. Cannot invoke {func.__name__}.'
            )
    return wrapper


def if_app_connected(func):
    """
    Decorator which raises if no apps connected.

    Args:
        func (callable): The function to be wrapped

    Returns:
        wrapper (callable): The decorated function
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.app is None:
            raise ValueError('No applications connected. Invoke connect_to_app first.')
        return func(self, *args, **kwargs)
    return wrapper
