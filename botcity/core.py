import os
import time
import webbrowser

import pyautogui

from .utils import ensure_state, only_if_element, is_retina

pyautogui.useImageNotFoundException(True)


@ensure_state
def add_image(label, path, *, state=None):
    """
    Add an image into the state image map.

    Args:
        label (str): The image identifier
        path (str): The path for the image on disk
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    state.map_images[label] = path


def browse(url, location=0):
    """
    Invoke the default browser passing an URL

    Args:
        url (str):  The URL to be visited.
        location (int): If possible, open url in a location determined by new:
                        * 0: the same browser window (the default)
                        * 1: a new browser window
                        * 2: a new browser page ("tab")

    Returns:
        bool: Whether or not the request was successful
    """
    status = webbrowser.open(url, location)
    return status


@ensure_state
def find(label, *, state=None, **kwargs):
    """
    Find an element defined by label on screen.

    Args:
        label (str): The image identifier
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
        **kwargs: Arbitrary keyword arguments that are forwarded to lower level find function.

    Returns:
        element (NamedTuple): The element coordinates
    """
    ele = pyautogui.locateOnScreen(state.map_images[label], **kwargs)
    if is_retina():
        ele = ele._replace(left=ele.left/2.0, top=ele.top/2.0)
    state.element = ele
    return state.element


def screenshot(filepath=""):
    """
    Capture a screenshot and save it to a file if filepath is informed.

    Args:
        filepath (str):  Filepath for the screenshot file.

    Returns:
        Image: The screenshot Image object
    """
    img = pyautogui.screenshot(filepath)
    return img


@only_if_element
@ensure_state
def click(*, state=None):
    """
    Click on the element.

    Args:
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
        **kwargs: Arbitrary keyword arguments that are forwarded to lower level find function.

    """
    pyautogui.click(state.element.left, state.element.top)


@ensure_state
def click_relative(x, y, *, state=None):
    """
    Click relative to the element.

    Args:
        x (int, float): The relative distance for the X axis
        y (int, float): The relative distance for the Y axis
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    pyautogui.click(state.element.left+x, state.element.top+y)


def enter():
    """
    Emulate Enter keypress.
    """
    pyautogui.press("enter")


def tab():
    """
    Emulate Tab keypress.
    """
    pyautogui.press("tab")


def sleep(interval):
    """
    Delay execution for a given amount of seconds.

    Args:
        interval (float): The interval for the delay. Use float for subsecond precision.
    """
    time.sleep(interval)


def type_text(text):
    """
    Emulate the typing of the given text.

    Args:
        text (str): The text to be typed
    """
    pyautogui.typewrite(text)


def execute(file_path):
    """
    Invoke the system handler to open the given file.

    Args:
        file_path (str): The path for the file to be executed
    """
    os.startfile(file_path)


# Java Aliases
addImage = add_image
clickRelative = click_relative
typeText = type_text
