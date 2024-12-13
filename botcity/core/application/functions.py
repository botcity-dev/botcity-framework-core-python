import time
from typing import Union
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import Application, WindowSpecification
from .utils import Backend
from .. import config


def connect(backend=Backend.WIN_32, timeout=60000, **connection_selectors) -> Application:
    """
    Connects to an instance of an open application.
    Use this method to be able to access application windows and elements.

    Args:
        backend (Backend, optional): The accessibility technology defined in the Backend class
            that could be used for your application. Defaults to Backend.WIN_32 ('win32').
        timeout (int, optional): Maximum wait time (ms) to wait for connection.
            Defaults to 60000ms (60s).
        **connection_selectors: Attributes that can be used to connect to an application.
            [See more details about the available selectors\
            ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/).

    Returns
        app (Application): The Application/Window instance.
    """
    connect_exception = None
    start_time = time.time()
    while True:
        elapsed_time = (time.time() - start_time) * 1000
        if elapsed_time > timeout:
            if connect_exception:
                raise connect_exception
            return None
        try:
            app = Application(backend=backend).connect(**connection_selectors)
            return app
        except Exception as e:
            connect_exception = e
            time.sleep(config.DEFAULT_SLEEP_AFTER_ACTION/1000.0)


def find_window(app: Union[Application, WindowSpecification],
                waiting_time=10000, **selectors) -> WindowSpecification:
    """
    Find a window of the currently connected application using the available selectors.

    Args:
        app (Application | WindowSpecification): The connected application.
        waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
            Defaults to 10000ms (10s).
        **selectors: Attributes that can be used to filter an element.
            [See more details about the available selectors\
            ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/).

    Returns
        dialog (WindowSpecification): The window or control found.
    """
    try:
        dialog = app.window(**selectors)
        dialog.wait(wait_for='exists ready', timeout=waiting_time / 1000.0)
        return dialog
    except (TimeoutError, ElementNotFoundError):
        return None


def find_element(app: Union[Application, WindowSpecification],
                 from_parent_window: WindowSpecification = None,
                 waiting_time=10000, **selectors) -> WindowSpecification:
    """
    Find a element of the currently connected application using the available selectors.
    You can pass the context window where the element is contained.

    Args:
        app (Application | WindowSpecification): The connected application.
        from_parent_window (WindowSpecification, optional): The element's parent window.
        waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
            Defaults to 10000ms (10s).
        **selectors: Attributes that can be used to filter an element.
            [See more details about the available selectors\
            ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/).

    Returns
        element (WindowSpecification): The element/control found.
    """
    try:
        if not from_parent_window:
            element = find_window(app, waiting_time, **selectors)
        else:
            element = from_parent_window.child_window(**selectors)
            element.wait(wait_for='exists ready', timeout=waiting_time / 1000.0)
        return element
    except (TimeoutError, ElementNotFoundError):
        return None
