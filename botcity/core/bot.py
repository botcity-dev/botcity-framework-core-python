import os
import functools
import multiprocessing
import platform
import random
import subprocess
import time
import webbrowser

import pyautogui
import pyperclip
from PIL import Image

from botcity.base import BaseBot, State
from botcity.base.utils import is_retina, only_if_element
from . import config, os_compat

try:
    from botcity.maestro import BotMaestroSDK
    MAESTRO_AVAILABLE = True
except ImportError:
    MAESTRO_AVAILABLE = False


class DesktopBot(BaseBot):
    """
    Base class for Desktop Bots.
    Users must implement the `action` method in their classes.

    Attributes:
        state (State): The internal state of this bot.
        maestro (BotMaestroSDK): an instance to interact with the BotMaestro server.

    """

    def __init__(self):
        super().__init__()
        self.state = State()
        self.maestro = BotMaestroSDK() if MAESTRO_AVAILABLE else None
        self._interval = 0.005 if platform.system() == "Darwin" else 0.0
        # For parity with Java
        self.addImage = self.add_image
        self.getImageFromMap = self.get_image_from_map
        self.getLastElement = self.get_last_element
        self.getScreenShot = self.get_screenshot
        self.screenCut = self.screen_cut
        self.saveScreenshot = self.save_screenshot
        self.getCoordinates = self.get_element_coords
        self.getElementCoords = self.get_element_coords
        self.getElementCoordsCentered = self.get_element_coords_centered
        self.find = self.find_until
        self.findUntil = self.find_until
        self.findText = self.find_text
        self.findLastUntil = self.find_until

        # Java API compatibility
        self.clickOn = self.click_on
        self.getLastX = self.get_last_x
        self.getLastY = self.get_last_y
        self.mouseMove = self.mouse_move
        self.clickAt = self.click_at
        self.doubleclick = self.double_click
        self.doubleClick = self.double_click
        self.doubleClickRelative = self.double_click_relative
        self.tripleClick = self.triple_click
        self.tripleClickRelative = self.triple_click_relative
        self.scrollDown = self.scroll_down
        self.scrollUp = self.scroll_up
        self.moveTo = self.mouse_move
        self.moveRelative = self.move_relative
        self.moveRandom = self.move_random
        self.moveAndClick = self.click
        self.rightClick = self.right_click
        self.rightClickAt = self.right_click_at
        self.rightClickRelative = self.right_click_relative
        self.moveAndRightClick = self.right_click
        pyperclip.determine_clipboard()

    ##########
    # Display
    ##########

    def add_image(self, label, path):
        """
        Add an image into the state image map.

        Args:
            label (str): The image identifier
            path (str): The path for the image on disk
        """
        self.state.map_images[label] = path

    def get_image_from_map(self, label):
        """
        Return an image from teh state image map.

        Args:
            label (str): The image identifier

        Returns:
            Image: The Image object
        """
        path = self.state.map_images.get(label)
        if not path:
            raise KeyError('Invalid label for image map.')
        img = Image.open(path)
        return img

    def find_multiple(self, labels, x=None, y=None, width=None, height=None, *,
                      threshold=None, matching=0.9, waiting_time=10000, best=True, grayscale=False):
        """
        Find multiple elements defined by label on screen until a timeout happens.

        Args:
            labels (list): A list of image identifiers
            x (int, optional): Search region start position x. Defaults to 0.
            y (int, optional): Search region start position y. Defaults to 0.
            width (int, optional): Search region width. Defaults to screen width.
            height (int, optional): Search region height. Defaults to screen height.
            threshold (int, optional): The threshold to be applied when doing grayscale search.
                Defaults to None.
            matching (float, optional): The matching index ranging from 0 to 1.
                Defaults to 0.9.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            best (bool, optional): Whether or not to keep looking until the best matching is found.
                Defaults to True.
            grayscale (bool, optional): Whether or not to convert to grayscale before searching.
                Defaults to False.

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
        paths = [self._search_image_file(la) for la in labels]
        paths = [self._image_path_as_image(la) for la in paths]

        if threshold:
            # TODO: Figure out how we should do threshold
            print('Threshold not yet supported')

        if not best:
            # TODO: Implement best=False.
            print('Warning: Ignoring best=False for now. It will be supported in the future.')

        start_time = time.time()
        n_cpus = multiprocessing.cpu_count() - 1

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return _to_dict(labels, results)

            haystack = pyautogui.screenshot()
            helper = functools.partial(self._find_multiple_helper, haystack, region, matching, grayscale)

            with multiprocessing.Pool(processes=n_cpus) as pool:
                results = pool.map(helper, paths)

            results = [self._fix_retina_element(r) for r in results]
            if None in results:
                continue
            else:
                return _to_dict(labels, results)

    def _fix_retina_element(self, ele):
        if not is_retina():
            return ele

        if ele is not None:
            if is_retina():
                ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
            return ele

    def _find_multiple_helper(self, haystack, region, confidence, grayscale, needle):
        ele = pyautogui.locate(needle, haystack, region=region, confidence=confidence, grayscale=grayscale)
        return ele

    def find(self, label, x=None, y=None, width=None, height=None, *, threshold=None,
             matching=0.9, waiting_time=10000, best=True, grayscale=False):
        """
        Find an element defined by label on screen until a timeout happens.

        Args:
            label (str): The image identifier
            x (int, optional): Search region start position x. Defaults to 0.
            y (int, optional): Search region start position y. Defaults to 0.
            width (int, optional): Search region width. Defaults to screen width.
            height (int, optional): Search region height. Defaults to screen height.
            threshold (int, optional): The threshold to be applied when doing grayscale search.
                Defaults to None.
            matching (float, optional): The matching index ranging from 0 to 1.
                Defaults to 0.9.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            best (bool, optional): Whether or not to keep looking until the best matching is found.
                Defaults to True.
            grayscale (bool, optional): Whether or not to convert to grayscale before searching.
                Defaults to False.

        Returns:
            element (NamedTuple): The element coordinates. None if not found.
        """
        return self.find_until(label, x=x, y=y, width=width, height=height, threshold=threshold,
                               matching=matching, waiting_time=waiting_time, best=best, grayscale=grayscale)

    def find_until(self, label, x=None, y=None, width=None, height=None, *,
                   threshold=None, matching=0.9, waiting_time=10000, best=True, grayscale=False):
        """
        Find an element defined by label on screen until a timeout happens.

        Args:
            label (str): The image identifier
            x (int, optional): Search region start position x. Defaults to 0.
            y (int, optional): Search region start position y. Defaults to 0.
            width (int, optional): Search region width. Defaults to screen width.
            height (int, optional): Search region height. Defaults to screen height.
            threshold (int, optional): The threshold to be applied when doing grayscale search.
                Defaults to None.
            matching (float, optional): The matching index ranging from 0 to 1.
                Defaults to 0.9.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            best (bool, optional): Whether or not to keep looking until the best matching is found.
                Defaults to True.
            grayscale (bool, optional): Whether or not to convert to grayscale before searching.
                Defaults to False.

        Returns:
            element (NamedTuple): The element coordinates. None if not found.
        """
        self.state.element = None
        screen_w, screen_h = pyautogui.size()
        x = x or 0
        y = y or 0
        w = width or screen_w
        h = height or screen_h

        region = (x, y, w, h)

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        if threshold:
            # TODO: Figure out how we should do threshold
            print('Threshold not yet supported')

        if not best:
            # TODO: Implement best=False.
            print('Warning: Ignoring best=False for now. It will be supported in the future.')

        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return None

            ele = pyautogui.locateOnScreen(element_path, region=region, confidence=matching,
                                           grayscale=grayscale)
            if ele is not None:
                if is_retina():
                    ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
                self.state.element = ele
                return ele

    def find_all(self, label, x=None, y=None, width=None, height=None, *,
                 threshold=None, matching=0.9, waiting_time=10000, grayscale=False):
        """
        Find all elements defined by label on screen until a timeout happens.

        Args:
            label (str): The image identifier
            x (int, optional): Search region start position x. Defaults to 0.
            y (int, optional): Search region start position y. Defaults to 0.
            width (int, optional): Search region width. Defaults to screen width.
            height (int, optional): Search region height. Defaults to screen height.
            threshold (int, optional): The threshold to be applied when doing grayscale search.
                Defaults to None.
            matching (float, optional): The matching index ranging from 0 to 1.
                Defaults to 0.9.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            grayscale (bool, optional): Whether or not to convert to grayscale before searching.
                Defaults to False.

        Returns:
            elements (collections.Iterable[NamedTuple]): A generator with all element coordinates fount.
                None if not found.
        """
        def deduplicate(elems):
            def find_same(item, items):
                x_start = item.left
                x_end = item.left + item.width
                y_start = item.top
                y_end = item.top + item.height
                similars = []
                for itm in items:
                    if itm == item:
                        continue
                    if (itm.left >= x_start and itm.left < x_end)\
                            and (itm.top >= y_start and itm.top < y_end):
                        similars.append(itm)
                        continue
                return similars

            index = 0
            while True:
                try:
                    dups = find_same(elems[index], elems[index:])
                    for d in dups:
                        elems.remove(d)
                    index += 1
                except IndexError:
                    break
            return elems

        self.state.element = None
        screen_w, screen_h = pyautogui.size()
        x = x or 0
        y = y or 0
        w = width or screen_w
        h = height or screen_h

        region = (x, y, w, h)

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        if threshold:
            # TODO: Figure out how we should do threshold
            print('Threshold not yet supported')

        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return None

            eles = pyautogui.locateAllOnScreen(element_path, region=region, confidence=matching,
                                               grayscale=grayscale)
            if not eles:
                continue
            eles = deduplicate(list(eles))
            for ele in eles:
                if ele is not None:
                    if is_retina():
                        ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
                    self.state.element = ele
                    yield ele
            break

    def find_text(self, label, x=None, y=None, width=None, height=None, *, threshold=None, matching=0.9,
                  waiting_time=10000, best=True):
        """
        Find an element defined by label on screen until a timeout happens.

        Args:
            label (str): The image identifier
            x (int, optional): Search region start position x. Defaults to 0.
            y (int, optional): Search region start position y. Defaults to 0.
            width (int, optional): Search region width. Defaults to screen width.
            height (int, optional): Search region height. Defaults to screen height.
            threshold (int, optional): The threshold to be applied when doing grayscale search.
                Defaults to None.
            matching (float, optional): The matching index ranging from 0 to 1.
                Defaults to 0.9.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            best (bool, optional): Whether or not to keep looking until the best matching is found.
                Defaults to True.

        Returns:
            element (NamedTuple): The element coordinates. None if not found.
        """
        return self.find_until(label, x, y, width, height, threshold=threshold, matching=matching,
                               waiting_time=waiting_time, best=best, grayscale=True)

    def get_last_element(self):
        """
        Return the last element found.

        Returns:
            element (NamedTuple): The element coordinates (left, top, width, height)
        """
        return self.state.element

    def display_size(self):
        """
        Returns the display size in pixels.

        Returns:
            size (Tuple): The screen dimension (width and height) in pixels.
        """
        screen_size = pyautogui.size()
        return screen_size.width, screen_size.height

    def screenshot(self, filepath=None, region=None):
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

    def get_screenshot(self, filepath=None, region=None):
        """
        Capture a screenshot.

        Args:
            filepath (str, optional): The filepath in which to save the screenshot. Defaults to None.
            region (tuple, optional): Bounding box containing left, top, width and height to crop screenshot.

        Returns:
            Image: The screenshot Image object
        """
        return self.screenshot(filepath, region)

    def screen_cut(self, x, y, width=None, height=None):
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

    def save_screenshot(self, path):
        """
        Saves a screenshot in a given path.

        Args:
            path (str): The filepath in which to save the screenshot

        """
        pyautogui.screenshot(path)

    def get_element_coords(self, label, x=None, y=None, width=None, height=None, matching=0.9, best=True):
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

        Returns:
            coords (Tuple): A tuple containing the x and y coordinates for the element.
        """
        self.state.element = None
        screen_size = pyautogui.size()
        x = x or 0
        y = y or 0
        width = width or screen_size.width
        height = height or screen_size.height
        region = (x, y, width, height)

        if not best:
            print('Warning: Ignoring best=False for now. It will be supported in the future.')

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        ele = pyautogui.locateOnScreen(element_path, region=region, confidence=matching)
        if ele is None:
            return None, None
        if is_retina():
            ele = ele._replace(left=ele.left / 2.0, top=ele.top / 2.0)
        self.state.element = ele
        return ele.left, ele.top

    def get_element_coords_centered(self, label, x=None, y=None, width=None, height=None,
                                    matching=0.9, best=True):
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

        Returns:
            coords (Tuple): A tuple containing the x and y coordinates for the center of the element.
        """
        self.get_element_coords(label, x, y, width, height, matching, best)
        return self.state.center()

    #########
    # Browser
    #########

    def browse(self, url, location=0):
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

    #######
    # Mouse
    #######

    def click_on(self, label):
        """
        Click on the element.

        Args:
            label (str): The image identifier
        """
        x, y = self.get_element_coords_centered(label)
        if None in (x, y):
            raise ValueError(f'Element not available. Cannot find {label}.')
        os_compat.click(x, y)

    def get_last_x(self):
        """
        Get the last X position for the mouse.

        Returns:
            x (int): The last x position for the mouse.
        """
        return pyautogui.position().x

    def get_last_y(self):
        """
        Get the last Y position for the mouse.

        Returns:
            y (int): The last y position for the mouse.
        """
        return pyautogui.position().y

    def mouse_move(self, x, y):
        """
        Mouse the move to the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate

        """
        pyautogui.moveTo(x, y)

    def click_at(self, x, y):
        """
        Click at the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate
        """
        os_compat.click(x, y)

    @only_if_element
    def click(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
              clicks=1, interval_between_clicks=0, button='left'):
        """
        Click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            clicks (int, optional): Number of times to click. Defaults to 1.
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        x, y = self.state.center()
        os_compat.click(x, y, clicks=clicks, button=button, interval=interval_between_clicks/1000.0)
        self.sleep(wait_after)

    @only_if_element
    def click_relative(self, x, y, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
                       clicks=1, interval_between_clicks=0, button='left'):
        """
        Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            wait_after (int, optional): Interval to wait after clicking on the element.
            clicks (int, optional): Number of times to click. Defaults to 1.
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        x = self.state.x() + x
        y = self.state.y() + y
        os_compat.click(x, y, clicks=clicks, button=button, interval=interval_between_clicks/1000.0)
        self.sleep(wait_after)

    @only_if_element
    def double_click(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Double Click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
        """
        self.click(wait_after=wait_after, clicks=2)

    @only_if_element
    def double_click_relative(self, x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Double Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.

        """
        self.click_relative(x, y, wait_after=wait_after, clicks=2, interval_between_clicks=interval_between_clicks)

    @only_if_element
    def triple_click(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Triple Click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
        """
        self.click(wait_after=wait_after, clicks=3)

    @only_if_element
    def triple_click_relative(self, x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Triple Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.

        """
        self.click_relative(x, y, wait_after=wait_after, clicks=3, interval_between_clicks=interval_between_clicks)

    def mouse_down(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, button='left'):
        """
        Holds down the requested mouse button.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        pyautogui.mouseDown(button=button)
        self.sleep(wait_after)

    def mouse_up(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, button='left'):
        """
        Releases the requested mouse button.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        pyautogui.mouseUp(button=button)
        self.sleep(wait_after)

    def scroll_down(self, clicks):
        """
        Scroll Down n clicks

        Args:
            clicks (int): Number of times to scroll down.
        """
        pyautogui.scroll(-1 * clicks)

    def scroll_up(self, clicks):
        """
        Scroll Up n clicks

        Args:
            clicks (int): Number of times to scroll up.
        """
        pyautogui.scroll(clicks)

    @only_if_element
    def move(self):
        """
        Move to the center position of last found item.
        """
        x, y = self.state.center()
        pyautogui.moveTo(x, y)

    def move_relative(self, x, y):
        """
        Move the mouse relative to its current position.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset

        """
        x = self.get_last_x() + x
        y = self.get_last_y() + y
        pyautogui.moveTo(x, y)

    def move_random(self, range_x, range_y):
        """
        Move randomly along the given x, y range.

        Args:
            range_x (int): Horizontal range
            range_y (int): Vertical range

        """
        x = int(random.random() * range_x)
        y = int(random.random() * range_y)
        pyautogui.moveTo(x, y)

    @only_if_element
    def right_click(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *,
                    clicks=1, interval_between_clicks=0):
        """
        Right click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            clicks (int, optional): Number of times to click. Defaults to 1.
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        """
        x, y = self.state.center()
        os_compat.click(x, y, clicks=clicks, button='right', interval=interval_between_clicks/1000.0)
        self.sleep(wait_after)

    def right_click_at(self, x, y):
        """
        Right click at the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate
        """
        os_compat.click(x, y, button='right')

    @only_if_element
    def right_click_relative(self, x, y, interval_between_clicks=0, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Right Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.
        """
        self.click_relative(x, y, wait_after=wait_after, clicks=3, interval_between_clicks=interval_between_clicks,
                            button='right')

    ##########
    # Keyboard
    ##########

    def type_key(self, text, interval=0):
        """
        Type a text char by char (individual key events).

        Args:
            text (str): text to be typed.
            interval (int, optional): interval (ms) between each key press. Defaults to 0

        """
        self.kb_type(text=text, interval=interval/1000.0)

    def kb_type(self, text, interval=0):
        """
        Type a text char by char (individual key events).

        Args:
            text (str): text to be typed.
            interval (int, optional): interval (ms) between each key press. Defaults to 0

        """
        pyautogui.write(text, interval=interval/1000.0)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def paste(self, text=None, wait=0):
        """
        Paste content from the clipboard.

        Args:
            text (str, optional): The text to be pasted. Defaults to None
            wait (int, optional): Wait interval (ms) after task
        """
        if text:
            pyperclip.copy(text)
        self.control_v()

    def copy_to_clipboard(self, text, wait=0):
        """
        Copy content to the clipboard.

        Args:
            text (str): The text to be copied.
            wait (int, optional): Wait interval (ms) after task
        """
        pyperclip.copy(text)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def tab(self, wait=0):
        """
        Press key Tab

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('tab')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def enter(self, wait=0):
        """
        Press key Enter

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('enter')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_right(self, wait=0):
        """
        Press key Right

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('right')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_enter(self, wait=0):
        """
        Press key Enter

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.enter(wait)

    def key_end(self, wait=0):
        """
        Press key End

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('end')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_esc(self, wait=0):
        """
        Press key Esc

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('esc')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def _key_fx(self, idx, wait=0):
        """
        Press key F[idx] where idx is a value from 1 to 12

        Args:
            idx (int): F key index from 1 to 12
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press(f'f{idx}')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_f1(self, wait=0):
        self._key_fx(1, wait=wait)

    def key_f2(self, wait=0):
        self._key_fx(2, wait=wait)

    def key_f3(self, wait=0):
        self._key_fx(3, wait=wait)

    def key_f4(self, wait=0):
        self._key_fx(4, wait=wait)

    def key_f5(self, wait=0):
        self._key_fx(5, wait=wait)

    def key_f6(self, wait=0):
        self._key_fx(6, wait=wait)

    def key_f7(self, wait=0):
        self._key_fx(7, wait=wait)

    def key_f8(self, wait=0):
        self._key_fx(8, wait=wait)

    def key_f9(self, wait=0):
        self._key_fx(9, wait=wait)

    def key_f10(self, wait=0):
        self._key_fx(10, wait=wait)

    def key_f11(self, wait=0):
        self._key_fx(11, wait=wait)

    def key_f12(self, wait=0):
        self._key_fx(12, wait=wait)

    def hold_shift(self, wait=0):
        """
        Hold key Shift

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.keyDown('shift')
        self.sleep(wait)

    def release_shift(self):
        """
        Release key Shift.
        This method needs to be invoked after holding Shift or similar.
        """
        pyautogui.keyUp('shift')

    def alt_space(self, wait=0):
        """
        Press keys Alt+Space

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'space', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def maximize_window(self):
        """
        Shortcut to maximize window on Windows OS.
        """
        self.alt_space()
        self.sleep(1000)
        pyautogui.press('x')

    def type_keys_with_interval(self, interval, keys):
        """
        Press a sequence of keys. Hold the keys in the specific order and releases them.

        Args:
            interval (int): Interval (ms) in which to press and release keys
            keys (list): List of keys to be pressed
        """
        pyautogui.hotkey(*keys, interval=interval/1000.0)

    def type_keys(self, keys):
        """
        Press a sequence of keys. Hold the keys in the specific order and releases them.

        Args:
            keys (list): List of keys to be pressed
        """
        self.type_keys_with_interval(100, keys)

    def alt_e(self, wait=0):
        """
        Press keys Alt+E

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'e', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_r(self, wait=0):
        """
        Press keys Alt+R

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'r', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_f(self, wait=0):
        """
        Press keys Alt+F

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'f', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_u(self, wait=0):
        """
        Press keys Alt+U

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'u', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_f4(self, wait=0):
        """
        Press keys Alt+F4

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('alt', 'f4', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_c(self, wait=0):
        """
        Press keys CTRL+C

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'c', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)
        return self.get_clipboard()

    def control_v(self, wait=0):
        """
        Press keys CTRL+V

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'v', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_a(self, wait=0):
        """
        Press keys CTRL+A

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'a', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_f(self, wait=0):
        """
        Press keys CTRL+F

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'f', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_p(self, wait=0):
        """
        Press keys CTRL+P

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'p', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_u(self, wait=0):
        """
        Press keys CTRL+U

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'u', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_r(self, wait=0):
        """
        Press keys CTRL+R

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'r', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_t(self, wait=0):
        """
        Press keys CTRL+T

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 't', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_end(self, wait=0):
        """
        Press keys CTRL+End

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'end', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_home(self, wait=0):
        """
        Press keys CTRL+Home

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'home', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_w(self, wait=0):
        """
        Press keys CTRL+W

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'w', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_shift_p(self, wait=0):
        """
        Press keys CTRL+Shift+P

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'shift', 'p', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_shift_j(self, wait=0):
        """
        Press keys CTRL+Shift+J

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key = 'ctrl'
        if platform.system() == 'Darwin':
            key = 'command'
        pyautogui.hotkey(key, 'shift', 'j', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def shift_tab(self, wait=0):
        """
        Press keys Shift+Tab

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.hotkey('shift', 'tab', interval=self._interval)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def get_clipboard(self):
        """
        Get the current content in the clipboard.

        Returns:
            text (str): Current clipboard content
        """
        return pyperclip.paste()

    def type_left(self, wait=0):
        """
        Press Left key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('left')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_right(self, wait=0):
        """
        Press Right key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('right')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_down(self, wait=0):
        """
        Press Down key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('down')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_up(self, wait=0):
        """
        Press Up key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('up')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_windows(self, wait=0):
        """
        Press Win logo key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('win')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def page_up(self, wait=0):
        """
        Press Page Up key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('pageup')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def page_down(self, wait=0):
        """
        Press Page Down key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('pagedown')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def space(self, wait=0):
        """
        Press Space key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('space')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def backspace(self, wait=0):
        """
        Press Backspace key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('backspace')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def delete(self, wait=0):
        """
        Press Delete key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        pyautogui.press('delete')
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    ######
    # Misc
    ######

    def wait_for_file(self, path, timeout=10000):
        """
        Invoke the system handler to open the given file.

        Args:
            path (str): The path for the file to be executed
            timeout (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).

        Returns
            status (bool): Whether or not the file was available before the timeout
        """
        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > timeout:
                return False
            if os.path.isfile(path) and os.access(path, os.R_OK):
                return True
            self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def execute(self, file_path):
        """
        Invoke the system handler to open the given file.

        Args:
            file_path (str): The path for the file to be executed
        """
        if platform.system() == "Windows":
            os.startfile(file_path)
        else:
            subprocess.Popen(file_path.split(" "))

    def wait(self, interval):
        """
        Wait / Sleep for a given interval.

        Args:
            interval (int): Interval in milliseconds

        """
        time.sleep(interval / 1000.0)

    def sleep(self, interval):
        """
        Wait / Sleep for a given interval.

        Args:
            interval (int): Interval in milliseconds

        """
        self.wait(interval)
