import functools
import time
import multiprocessing
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
def find_multiple(labels, x=None, y=None, width=None, height=None, *,
                  threshold=None, matching=0.9, waiting_time=10000, best=True, grayscale=False, state=None):
    """
    Find multiple elements defined by label on screen until a timeout happens.

    Args:
        labels (list): A list of image identifiers
        x (int, optional): Search region start position x. Defaults to 0.
        y (int, optional): Search region start position y. Defaults to 0.
        width (int, optional): Search region width. Defaults to screen width.
        height (int, optional): Search region height. Defaults to screen height.
        threshold (int, optional): The threshold to be applied when doing grayscale search. Defaults to None.
        matching (float, optional): The matching index ranging from 0 to 1. Defaults to 0.9.
        waiting_time (int, optional): Maximum wait time (ms) to search for a hit. Defaults to 10000ms (10s).
        best (bool, optional): Whether or not to keep looking until the best matching is found. Defaults to True.
        grayscale (bool, optional): Whether or not to convert to grayscale before searching. Defaults to False.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        results (dict): A dictionary in which the key is the label and value are the element coordinates in a
           NamedTuple.
    """
    def _to_dict(lbs, elems):
        return {k: v for k, v in zip(lbs, elems)}

    screen_w, screen_h = pyautogui.size()
    x = x or 0
    y = y or 0
    w = width or screen_w
    h = height or screen_h

    region = (x, y, w, h)

    results = [None] * len(labels)
    paths = [state.map_images[la] for la in labels]

    if threshold:
        # TODO: Figure out how we should do threshold
        print('Threshold not yet supported')

    if not best:
        # TODO: Implement best=False.
        print('Warning: Ignoring best=False for now. It will be supported in the future.')

    start_time = time.time()
    n_cpus = multiprocessing.cpu_count()-1

    while True:
        elapsed_time = (time.time() - start_time)*1000
        if elapsed_time > waiting_time:
            return _to_dict(labels, results)

        haystack = pyautogui.screenshot()
        helper = functools.partial(__find_multiple_helper, haystack, region, matching, grayscale)

        with multiprocessing.Pool(processes=n_cpus) as pool:
            results = pool.map(helper, paths)

        results = [__fix_retina_element(r) for r in results]
        if None in results:
            continue
        else:
            return _to_dict(labels, results)


def __fix_retina_element(ele):
    if not is_retina():
        return ele

    if ele is not None:
        if is_retina():
            ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
        return ele


def __find_multiple_helper(haystack, region, confidence, grayscale, needle):
    ele = pyautogui.locate(needle, haystack, region=region, confidence=confidence, grayscale=grayscale)
    return ele


@ensure_state
def find_until(label, x=None, y=None, width=None, height=None, *,
               threshold=None, matching=0.9, waiting_time=10000, best=True, grayscale=False, state=None):
    """
    Find an element defined by label on screen until a timeout happens.

    Args:
        label (str): The image identifier
        x (int, optional): Search region start position x. Defaults to 0.
        y (int, optional): Search region start position y. Defaults to 0.
        width (int, optional): Search region width. Defaults to screen width.
        height (int, optional): Search region height. Defaults to screen height.
        threshold (int, optional): The threshold to be applied when doing grayscale search. Defaults to None.
        matching (float, optional): The matching index ranging from 0 to 1. Defaults to 0.9.
        waiting_time (int, optional): Maximum wait time (ms) to search for a hit. Defaults to 10000ms (10s).
        best (bool, optional): Whether or not to keep looking until the best matching is found. Defaults to True.
        grayscale (bool, optional): Whether or not to convert to grayscale before searching. Defaults to False.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        element (NamedTuple): The element coordinates. None if not found.
    """
    state.element = None
    screen_w, screen_h = pyautogui.size()
    x = x or 0
    y = y or 0
    w = width or screen_w
    h = height or screen_h

    region = (x, y, w, h)

    element_path = state.map_images[label]

    if threshold:
        # TODO: Figure out how we should do threshold
        print('Threshold not yet supported')

    if not best:
        # TODO: Implement best=False.
        print('Warning: Ignoring best=False for now. It will be supported in the future.')

    start_time = time.time()

    while True:
        elapsed_time = (time.time() - start_time)*1000
        if elapsed_time > waiting_time:
            return None

        ele = pyautogui.locateOnScreen(element_path, region=region, confidence=matching, grayscale=grayscale)
        if ele is not None:
            if is_retina():
                ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
            state.element = ele
            return ele


@ensure_state
def find_text(label, x=None, y=None, width=None, height=None, *, threshold=None, matching=0.9, waiting_time=10000,
              best=True, state=None):
    """
    Find an element defined by label on screen until a timeout happens.

    Args:
        label (str): The image identifier
        x (int, optional): Search region start position x. Defaults to 0.
        y (int, optional): Search region start position y. Defaults to 0.
        width (int, optional): Search region width. Defaults to screen width.
        height (int, optional): Search region height. Defaults to screen height.
        threshold (int, optional): The threshold to be applied when doing grayscale search. Defaults to None.
        matching (float, optional): The matching index ranging from 0 to 1. Defaults to 0.9.
        waiting_time (int, optional): Maximum wait time (ms) to search for a hit. Defaults to 10000ms (10s).
        best (bool, optional): Whether or not to keep looking until the best matching is found. Defaults to True.
        state (State, optional): An instance of BaseState. If not provided, the singleton State is used.

    Returns:
        element (NamedTuple): The element coordinates. None if not found.
    """
    return find_until(label, x, y, width, height, threshold=threshold, matching=matching,
                      waiting_time=waiting_time, best=best, grayscale=True, state=state)


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


def display_size():
    """
    Returns the display size in pixels.

    Returns:
        size (Tuple): The screen dimension (width and height) in pixels.
    """
    screen_size = pyautogui.size()
    return screen_size.width, screen_size.height


def screenshot(filepath=None, region=None):
    """
    Capture a screenshot.

    Args:
        filepath (str, optional): The filepath in which to save the screenshot. Defaults to None.
        region (tuple, optional): Bounding box containing left, top, width and height to crop screenshot.

    Returns:
        Image: The screenshot Image object
    """
    img = pyautogui.screenshot(filepath, region)
    return img


def get_screenshot(filepath=None, region=None):
    """
    Capture a screenshot.

    Args:
        filepath (str, optional): The filepath in which to save the screenshot. Defaults to None.
        region (tuple, optional): Bounding box containing left, top, width and height to crop screenshot.

    Returns:
        Image: The screenshot Image object
    """
    return screenshot(filepath, region)


def screen_cut(x, y, width=None, height=None):
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
    screen_size = pyautogui.size()
    x = x or 0
    y = y or 0
    width = width or screen_size.width
    height = height or screen_size.height
    img = pyautogui.screenshot(region=(x, y, width, height))
    return img


def save_screenshot(path):
    """
    Saves a screenshot in a given path.

    Args:
        path (str): The filepath in which to save the screenshot

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
    state.element = None
    screen_size = pyautogui.size()
    x = x or 0
    y = y or 0
    width = width or screen_size.width
    height = height or screen_size.height
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


addImage = add_image
getImageFromMap = get_image_from_map
getLastElement = get_last_element
getScreenShot = get_screenshot
screenCut = screen_cut
saveScreenshot = save_screenshot
getCoordinates = get_element_coords
getElementCoords = get_element_coords
getElementCoordsCentered = get_element_coords_centered
find = find_until
findUntil = find_until
findText = find_text
findLastUntil = find_until
