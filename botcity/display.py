import pyautogui
from PIL import Image

from .utils import ensure_state, is_retina


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


@ensure_state
def get_image_from_map(label, *, state=None):
    """
    Return an image from teh state image map.

    Args:
        label (str): The image identifier
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        Image: The Image object
    """
    path = state.map_images.get(label)
    if not path:
        raise KeyError('Invalid label for image map.')
    img = Image.open(path)
    return img


@ensure_state
def get_last_element(*, state=None):
    """
    Return the last element found.

    Args:
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        element (NamedTuple): The element coordinates (left, top, width, height)
    """
    return state.element


def screenshot(filepath, region):
    """
    Capture a screenshot.

    Returns:
        Image: The screenshot Image object
    """
    img = pyautogui.screenshot()
    return img


def get_screenshot():
    """
    Capture a screenshot.

    Returns:
        Image: The screenshot Image object
    """
    return screenshot()


def screen_cut(x, y, width, height):
    """
    Capture a screenshot from a region of the screen.

    Args:
        x (int): region start position x
        y (int): region start position y
        width (int): region width
        height (int): region height

    Returns:
        Image: The screenshot Image object
    """
    img = pyautogui.screenshot(region=(x, y, width, height))
    return img


def save_screenshot(path):
    """
    Saves a screenshot in a given path.

    Args:
        path (str):

    """
    pyautogui.screenshot(path)


@ensure_state
def get_element_coords(label, x=None, y=None, width=None, height=None, matching=0.9, best=True, *, state=None):
    """
    Find an element defined by label on screen and returns its coordinates.

    Args:
        label (str): The image identifier
        x (int, optional): X (Left) coordinate of the search area.
        y (int, optional): Y (Top) coordinate of the search area.
        width (int, optional): Width of the search area.
        height (int, optional): Height of the search area.
        matching (float, optional): Minimum score to consider a match in the element image recognition process.
            Defaults to 0.9.
        best (bool, optional): Whether or not to search for the best value. If False the method returns on
            the first find. Defaults to True.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        coords (Tuple): A tuple containing the x and y coordinates for the element.
    """
    screen_size = pyautogui.size()
    x = x or 0
    y = y or 0
    width = width or screen_size.width
    height = height or screen_size.width
    region = (x, y, width, height)

    if not best:
        print('Warning: Ignoring best=False for now. It will be supported in the future.')

    ele = pyautogui.locateOnScreen(state.map_images[label], region=region, confidence=matching)
    if is_retina():
        ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
    state.element = ele
    return ele.left, ele.top


@ensure_state
def get_element_coords_centered(label, x=None, y=None, width=None, height=None,
                                matching=0.9, best=True, *, state=None):
    """
    Find an element defined by label on screen and returns its centered coordinates.

    Args:
        label (str): The image identifier
        x (int, optional): X (Left) coordinate of the search area.
        y (int, optional): Y (Top) coordinate of the search area.
        width (int, optional): Width of the search area.
        height (int, optional): Height of the search area.
        matching (float, optional): Minimum score to consider a match in the element image recognition process.
            Defaults to 0.9.
        best (bool, optional): Whether or not to search for the best value. If False the method returns on
            the first find. Defaults to True.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        coords (Tuple): A tuple containing the x and y coordinates for the center of the element.
    """
    get_element_coords(label, x, y, width, height, matching, best, state=state)
    return state.center()


getImageFromMap = get_image_from_map
getLastElement = get_last_element
getScreenShot = get_screenshot
screenCut = screen_cut
saveScreenshot = save_screenshot
getElementCoords = get_element_coords
getElementCoordsCentered = get_element_coords_centered
