import pyautogui
import random

from .utils import ensure_state, only_if_element
from . import config


@ensure_state
@only_if_element
def click_on(label, *, state=None):
    """
    Click on the element.

    Args:
        label (str): The image identifier
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    from .display import get_element_coords_centered
    x, y = get_element_coords_centered(label, state=state)
    pyautogui.click(x, y)


@ensure_state
def get_last_x():
    """
    Get the last X position for the mouse.

    Returns:
        x (int): The last x position for the mouse.
    """
    return pyautogui.position().x


def get_last_y():
    """
    Get the last Y position for the mouse.

    Returns:
        y (int): The last y position for the mouse.
    """
    return pyautogui.position().y


def mouse_move(x, y):
    """
    Mouse the move to the coordinate defined by x and y

    Args:
        x (int): The X coordinate
        y (int): The Y coordinate

    """
    pyautogui.moveTo(x, y)


def click_at(x, y):
    """
    Click at the coordinate defined by x and y

    Args:
        x (int): The X coordinate
        y (int): The Y coordinate
    """
    pyautogui.click(x, y)


@ensure_state
@only_if_element
def click(wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
          clicks=1, interval_between_clicks=0, button='left', state):
    """
    Click on the last found element.

    Args:
        wait_after (int, optional): Interval to wait after clicking on the element.
        clicks (int, optional): Number of times to click. Defaults to 1.
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    from .misc import sleep
    x, y = state.center()
    pyautogui.click(x, y, clicks=clicks, button=button, interval=interval_between_clicks)
    sleep(wait_after)


@ensure_state
@only_if_element
def click_relative(x, y, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
                   clicks=1, interval_between_clicks=0, button='left', state):
    """
    Click Relative on the last found element.

    Args:
        x (int): Horizontal offset
        y (int): Vertical offset
        wait_after (int, optional): Interval to wait after clicking on the element.
        clicks (int, optional): Number of times to click. Defaults to 1.
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    from .misc import sleep
    x = state.x() + x
    y = state.y() + y
    pyautogui.click(x, y, clicks=clicks, button=button, interval=interval_between_clicks)
    sleep(wait_after)


@ensure_state
@only_if_element
def double_click(wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, state):
    """
    Double Click on the last found element.

    Args:
        wait_after (int, optional): Interval to wait after clicking on the element.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    """
    x, y = state.center()
    click(x, y, wait_after=wait_after, click=2)


@ensure_state
@only_if_element
def double_click_relative(x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, state):
    """
    Double Click Relative on the last found element.

    Args:
        x (int): Horizontal offset
        y (int): Vertical offset
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        wait_after (int, optional): Interval to wait after clicking on the element.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    """
    x = state.x() + x
    y = state.y() + y
    click_relative(x, y, wait_after=wait_after, click=2, interval_between_clicks=interval_between_clicks)


@ensure_state
@only_if_element
def triple_click(wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, state):
    """
    Triple Click on the last found element.

    Args:
        wait_after (int, optional): Interval to wait after clicking on the element.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    """
    x, y = state.center()
    click(x, y, wait_after=wait_after, click=3)


@ensure_state
@only_if_element
def triple_click_relative(x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, state):
    """
    Triple Click Relative on the last found element.

    Args:
        x (int): Horizontal offset
        y (int): Vertical offset
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        wait_after (int, optional): Interval to wait after clicking on the element.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    """
    x = state.x() + x
    y = state.y() + y
    click_relative(x, y, wait_after=wait_after, click=3, interval_between_clicks=interval_between_clicks)


def scroll_down(clicks):
    """
    Scroll Down n clicks

    Args:
        clicks (int): Number of times to scroll down.
    """
    pyautogui.scroll(-1*clicks)


def scroll_up(clicks):
    """
    Scroll Up n clicks

    Args:
        clicks (int): Number of times to scroll up.
    """
    pyautogui.scroll(clicks)


@ensure_state
@only_if_element
def move(*, state):
    """
    Move to the center position of last found item.

    Args:
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    x, y = state.center()
    pyautogui.moveTo(x, y)


def move_relative(x, y):
    """
    Move the mouse relative to its current position.

    Args:
        x (int): Horizontal offset
        y (int): Vertical offset

    """
    x = get_last_x() + x
    y = get_last_y() + y
    pyautogui.moveTo(x, y)


def move_random(range_x, range_y):
    """
    Move randomly along the given x, y range.

    Args:
        range_x (int): Horizontal range
        range_y (int): Vertical range

    """
    x = int(random.random()*range_x)
    y = int(random.random()*range_y)
    pyautogui.moveTo(x, y)


@ensure_state
@only_if_element
def right_click(wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
                clicks=1, interval_between_clicks=0, state):
    """
    Right click on the last found element.

    Args:
        wait_after (int, optional): Interval to wait after clicking on the element.
        clicks (int, optional): Number of times to click. Defaults to 1.
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.
    """
    from .misc import sleep
    x, y = state.center()
    pyautogui.click(x, y, clicks=clicks, button='right', interval=interval_between_clicks)
    sleep(wait_after)


def right_click_at(x, y):
    """
    Right click at the coordinate defined by x and y

    Args:
        x (int): The X coordinate
        y (int): The Y coordinate
    """
    pyautogui.click(x, y, button='right')


@ensure_state
@only_if_element
def right_click_relative(x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, state):
    """
    Right Click Relative on the last found element.

    Args:
        x (int): Horizontal offset
        y (int): Vertical offset
        interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        wait_after (int, optional): Interval to wait after clicking on the element.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    """
    x = state.x() + x
    y = state.y() + y
    click_relative(x, y, wait_after=wait_after, click=3, interval_between_clicks=interval_between_clicks,
                   button='right')


# Java API compatibility
clickOn = click_on
getLastX = get_last_x
getLastY = get_last_y
mouseMove = mouse_move
clickAt = click_at
doubleclick = double_click
doubleClick = double_click
doubleClickRelative = double_click_relative
tripleClick = triple_click
tripleClickRelative = triple_click_relative
scrollDown = scroll_down
scrollUp = scroll_up
moveTo = mouse_move
moveRelative = move_relative
moveRandom = move_random
moveAndClick = click
rightClick = right_click
rightClickAt = right_click_at
rightClickRelative = right_click_relative
moveAndRightClick = right_click
