import functools
import os
import platform
import psutil
import random
import subprocess
import time
import webbrowser
from typing import Union, Tuple, Optional, List, Dict, Generator, Any

from numpy import ndarray

import pyperclip
from botcity.base import BaseBot, State
from botcity.base.utils import is_retina, only_if_element
from PIL import Image, ImageGrab
from psutil import Process
from pynput.keyboard import Controller as KbController
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Controller as MouseController

from . import config, cv2find
from .input_utils import _mouse_click, keys_map, mouse_map

try:
    from pywinauto.application import Application, WindowSpecification

    from .application.functions import connect, find_element, find_window
except ImportError:
    pass

from .application.utils import Backend, if_app_connected, if_windows_os

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
        self._app = None
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

        # Pynput mouse and kb controller
        self._kb_controller = KbController()
        self._mouse_controller = MouseController()

    @property
    def app(self) -> Union["Application", "WindowSpecification"]:
        """
        The connected application instance to be used.

        Returns:
            app (Application | WindowSpecification): The connected Application/Window instance.
        """
        return self._app

    @app.setter
    def app(self, app: Union["Application", "WindowSpecification"]):
        """
        The connected application instance to be used.

        Args:
            app (Application | WindowSpecification): The connected Application/Window instance.
        """
        self._app = app

    ##########
    # Display
    ##########

    def add_image(self, label: str, path: str) -> None:
        """
        Add an image into the state image map.

        Args:
            label (str): The image identifier
            path (str): The path for the image on disk
        """
        self.state.map_images[label] = path

    def get_image_from_map(self, label: str) -> Image.Image:
        """
        Return an image from teh state image map.

        Args:
            label (str): The image identifier

        Returns:
            Image: The Image object
        """
        path = self.state.map_images.get(label)
        if not path:
            raise KeyError("Invalid label for image map.")
        img = Image.open(path)
        return img

    def find_multiple(
        self,
        labels: List,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
        matching: float = 0.9,
        waiting_time: int = 10000,
        best: bool = True,
        grayscale: bool = False,
    ) -> Dict:
        """
        Find multiple elements defined by label on screen until a timeout happens.

        Args:
            labels (list): A list of image identifiers
            x (int): Search region start position x. Defaults to 0.
            y (int): Search region start position y. Defaults to 0.
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

        screen_w, screen_h = self._fix_display_size()
        w = width or screen_w
        h = height or screen_h

        region = (x, y, w, h)

        results = [None] * len(labels)
        paths = [self._search_image_file(la) for la in labels]
        paths = [self._image_path_as_image(la) for la in paths]

        if threshold:
            # TODO: Figure out how we should do threshold
            print("Threshold not yet supported")

        if not best:
            # TODO: Implement best=False.
            print(
                "Warning: Ignoring best=False for now. It will be supported in the future."
            )

        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return _to_dict(labels, results)

            haystack = self.screenshot()
            helper = functools.partial(
                self._find_multiple_helper, haystack, region, matching, grayscale
            )

            results = [helper(p) for p in paths]

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
                ele = ele._replace(
                    left=ele.left / 2.0,
                    top=ele.top / 2.0,
                    width=ele.width / 2.0,
                    height=ele.height / 2.0,
                )
            return ele

    def _fix_display_size(self) -> Tuple[int, int]:
        width, height = ImageGrab.grab().size

        if not is_retina():
            return width, height

        return int(width * 2), int(height * 2)

    def _find_multiple_helper(
        self,
        haystack: Image.Image,
        region: Tuple[int, int, int, int],
        confidence: float,
        grayscale: bool,
        needle: Union[Image.Image, ndarray, str],
    ) -> Union[cv2find.Box, None]:
        ele = cv2find.locate_all_opencv(
            needle, haystack, region=region, confidence=confidence, grayscale=grayscale
        )
        try:
            ele = next(ele)
        except StopIteration:
            ele = None
        return ele

    def find(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
        matching: float = 0.9,
        waiting_time: int = 10000,
        best: bool = True,
        grayscale: bool = False,
    ) -> Union[cv2find.Box, None]:
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
        return self.find_until(
            label,
            x=x,
            y=y,
            width=width,
            height=height,
            threshold=threshold,
            matching=matching,
            waiting_time=waiting_time,
            best=best,
            grayscale=grayscale,
        )

    def find_until(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
        matching: float = 0.9,
        waiting_time: int = 10000,
        best: bool = True,
        grayscale: bool = False,
    ) -> Union[cv2find.Box, None]:
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
        screen_w, screen_h = self._fix_display_size()
        x = x or 0
        y = y or 0
        w = width or screen_w
        h = height or screen_h

        region = (x, y, w, h)

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        if threshold:
            # TODO: Figure out how we should do threshold
            print("Threshold not yet supported")

        if not best:
            # TODO: Implement best=False.
            print(
                "Warning: Ignoring best=False for now. It will be supported in the future."
            )

        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return None

            haystack = self.get_screenshot()
            it = cv2find.locate_all_opencv(
                element_path,
                haystack_image=haystack,
                region=region,
                confidence=matching,
                grayscale=grayscale,
            )
            try:
                ele = next(it)
            except StopIteration:
                ele = None

            if ele is not None:
                ele = self._fix_retina_element(ele)
                self.state.element = ele
                return ele

    def find_all(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
        matching: float = 0.9,
        waiting_time: int = 10000,
        grayscale: bool = False,
    ) -> Generator[cv2find.Box, Any, None]:
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

        def deduplicate(
            elems: list[Generator[cv2find.Box, Any, None]]
        ) -> list[Generator[cv2find.Box, Any, None]]:
            def find_same(item, items):
                x_start = item.left
                x_end = item.left + item.width
                y_start = item.top
                y_end = item.top + item.height
                similars = []
                for itm in items:
                    if itm == item:
                        continue
                    if (itm.left >= x_start and itm.left < x_end) and (
                        itm.top >= y_start and itm.top < y_end
                    ):
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
        screen_w, screen_h = self._fix_display_size()
        x = x or 0
        y = y or 0
        w = width or screen_w
        h = height or screen_h

        region = (x, y, w, h)

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        if threshold:
            # TODO: Figure out how we should do threshold
            print("Threshold not yet supported")

        start_time = time.time()

        while True:
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > waiting_time:
                return None

            haystack = self.get_screenshot()
            eles = cv2find.locate_all_opencv(
                element_path,
                haystack_image=haystack,
                region=region,
                confidence=matching,
                grayscale=grayscale,
            )
            if not eles:
                continue
            eles = deduplicate(list(eles))
            for ele in eles:
                if ele is not None:
                    ele = self._fix_retina_element(ele)
                    self.state.element = ele
                    yield ele
            break

    def find_text(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        *,
        threshold: Optional[int] = None,
        matching: float = 0.9,
        waiting_time: int = 10000,
        best: bool = True,
    ) -> Union[cv2find.Box, None]:
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
        return self.find_until(
            label,
            x,
            y,
            width,
            height,
            threshold=threshold,
            matching=matching,
            waiting_time=waiting_time,
            best=best,
            grayscale=True,
        )

    def find_process(
        self, name: Optional[str] = None, pid: Optional[str] = None
    ) -> Union[Process, None]:
        """
        Find a process by name or PID

        Args:
            name (str): The process name.
            pid (str) or (int): The PID (Process Identifier).

        Return:
            process (psutil.Process): A Process instance.
        """
        for process in psutil.process_iter():
            try:
                if (name is not None and name in process.name()) or (
                    pid is not None and process.pid == pid
                ):
                    return process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None

    def terminate_process(self, process: Process) -> None:
        """
        Terminate the process via the received Process object.

        Args:
            process (psutil.Process): The process to terminate.
        """
        process.terminate()
        process.wait(10)
        if process.is_running():
            raise Exception("Terminate process failed")

    def get_last_element(self) -> cv2find.Box:
        """
        Return the last element found.

        Returns:
            element (NamedTuple): The element coordinates (left, top, width, height)
        """
        return self.state.element

    def display_size(self) -> Tuple[int, int]:
        """
        Returns the display size in pixels.

        Returns:
            size (Tuple): The screen dimension (width and height) in pixels.
        """
        width, height = self._fix_display_size()
        return width, height

    def screenshot(
        self,
        filepath: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Image.Image:
        """
        Capture a screenshot.

        Args:
            filepath (str, optional): The filepath in which to save the screenshot. Defaults to None.
            region (tuple, optional): Bounding box containing left, top, width and height to crop screenshot.

        Returns:
            Image: The screenshot Image object
        """
        if region:
            x, y, width, height = region
            width = x + width
            height = y + height
            region = (x, y, width, height)

        img = ImageGrab.grab(bbox=region)
        if filepath:
            img.save(filepath)
        return img

    def get_screenshot(
        self,
        filepath: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Image.Image:
        """
        Capture a screenshot.

        Args:
            filepath (str, optional): The filepath in which to save the screenshot. Defaults to None.
            region (tuple, optional): Bounding box containing left, top, width and height to crop screenshot.

        Returns:
            Image: The screenshot Image object
        """
        return self.screenshot(filepath, region)

    def screen_cut(
        self,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Image.Image:
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
        screen_w, screen_h = self._fix_display_size()

        width = width or screen_w
        height = height or screen_h
        img = self.screenshot(region=(x, y, width, height))
        return img

    def save_screenshot(self, path: str) -> None:
        """
        Saves a screenshot in a given path.

        Args:
            path (str): The filepath in which to save the screenshot

        """
        self.screenshot(path)

    def get_element_coords(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        matching: float = 0.9,
        best: bool = True,
    ) -> Union[Tuple[int, int], Tuple[None, None]]:
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
        screen_w, screen_h = self._fix_display_size()
        x = x or 0
        y = y or 0
        width = width or screen_w
        height = height or screen_h
        region = (x, y, width, height)

        if not best:
            print(
                "Warning: Ignoring best=False for now. It will be supported in the future."
            )

        element_path = self._search_image_file(label)
        element_path = self._image_path_as_image(element_path)

        haystack = self.get_screenshot()
        it = cv2find.locate_all_opencv(
            element_path,
            haystack_image=haystack,
            region=region,
            confidence=matching,
            grayscale=False,
        )
        try:
            ele = next(it)
        except StopIteration:
            ele = None

        if ele is None:
            return None, None
        ele = self._fix_retina_element(ele)
        self.state.element = ele
        return ele.left, ele.top

    def get_element_coords_centered(
        self,
        label: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        matching: float = 0.9,
        best: bool = True,
    ):
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
            raise ValueError(f"Element not available. Cannot find {label}.")
        _mouse_click(self._mouse_controller, x, y)

    def get_last_x(self):
        """
        Get the last X position for the mouse.

        Returns:
            x (int): The last x position for the mouse.
        """
        return self._mouse_controller.position[0]

    def get_last_y(self):
        """
        Get the last Y position for the mouse.

        Returns:
            y (int): The last y position for the mouse.
        """
        return self._mouse_controller.position[1]

    def mouse_move(self, x, y):
        """
        Move the mouse to the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate

        """
        self._mouse_controller.position = (x, y)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def click_at(self, x, y):
        """
        Click at the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate
        """
        _mouse_click(self._mouse_controller, x, y)

    @only_if_element
    def click(
        self,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
        *,
        clicks=1,
        interval_between_clicks=0,
        button="left",
    ):
        """
        Click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            clicks (int, optional): Number of times to click. Defaults to 1.
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        x, y = self.state.center()
        _mouse_click(
            self._mouse_controller, x, y, clicks, interval_between_clicks, button
        )
        self.sleep(wait_after)

    @only_if_element
    def click_relative(
        self,
        x,
        y,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
        *,
        clicks=1,
        interval_between_clicks=0,
        button="left",
    ):
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
        _mouse_click(
            self._mouse_controller, x, y, clicks, interval_between_clicks, button
        )
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
    def double_click_relative(
        self,
        x,
        y,
        interval_between_clicks=0,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
    ):
        """
        Double Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.

        """
        self.click_relative(
            x,
            y,
            wait_after=wait_after,
            clicks=2,
            interval_between_clicks=interval_between_clicks,
        )

    @only_if_element
    def triple_click(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION):
        """
        Triple Click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
        """
        self.click(wait_after=wait_after, clicks=3)

    @only_if_element
    def triple_click_relative(
        self,
        x,
        y,
        interval_between_clicks=0,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
    ):
        """
        Triple Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.

        """
        self.click_relative(
            x,
            y,
            wait_after=wait_after,
            clicks=3,
            interval_between_clicks=interval_between_clicks,
        )

    def mouse_down(
        self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, button="left"
    ):
        """
        Holds down the requested mouse button.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        mouse_button = mouse_map.get(button, None)
        self._mouse_controller.press(mouse_button)
        self.sleep(wait_after)

    def mouse_up(self, wait_after=config.DEFAULT_SLEEP_AFTER_ACTION, *, button="left"):
        """
        Releases the requested mouse button.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            button (str, optional): One of 'left', 'right', 'middle'. Defaults to 'left'
        """
        mouse_button = mouse_map.get(button, None)
        self._mouse_controller.release(mouse_button)
        self.sleep(wait_after)

    def scroll_down(self, clicks):
        """
        Scroll Down n clicks

        Args:
            clicks (int): Number of times to scroll down.
        """
        self._mouse_controller.scroll(0, -1 * clicks)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def scroll_up(self, clicks):
        """
        Scroll Up n clicks

        Args:
            clicks (int): Number of times to scroll up.
        """
        self._mouse_controller.scroll(0, clicks)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    @only_if_element
    def move(self):
        """
        Move to the center position of last found item.
        """
        x, y = self.state.center()
        self._mouse_controller.position = (x, y)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def move_relative(self, x, y):
        """
        Move the mouse relative to its current position.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset

        """
        x = self.get_last_x() + x
        y = self.get_last_y() + y
        self._mouse_controller.position = (x, y)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def move_random(self, range_x, range_y):
        """
        Move randomly along the given x, y range.

        Args:
            range_x (int): Horizontal range
            range_y (int): Vertical range

        """
        x = int(random.random() * range_x)
        y = int(random.random() * range_y)
        self._mouse_controller.position = (x, y)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    @only_if_element
    def right_click(
        self,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
        *,
        clicks=1,
        interval_between_clicks=0,
    ):
        """
        Right click on the last found element.

        Args:
            wait_after (int, optional): Interval to wait after clicking on the element.
            clicks (int, optional): Number of times to click. Defaults to 1.
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
        """
        x, y = self.state.center()
        _mouse_click(
            self._mouse_controller,
            x,
            y,
            clicks,
            interval_between_clicks,
            button="right",
        )
        self.sleep(wait_after)

    def right_click_at(self, x, y):
        """
        Right click at the coordinate defined by x and y

        Args:
            x (int): The X coordinate
            y (int): The Y coordinate
        """
        _mouse_click(self._mouse_controller, x, y, button="right")

    @only_if_element
    def right_click_relative(
        self,
        x,
        y,
        interval_between_clicks=0,
        wait_after=config.DEFAULT_SLEEP_AFTER_ACTION,
    ):
        """
        Right Click Relative on the last found element.

        Args:
            x (int): Horizontal offset
            y (int): Vertical offset
            interval_between_clicks (int, optional): The interval between clicks in ms. Defaults to 0.
            wait_after (int, optional): Interval to wait after clicking on the element.
        """
        self.click_relative(
            x,
            y,
            wait_after=wait_after,
            clicks=1,
            interval_between_clicks=interval_between_clicks,
            button="right",
        )

    ##########
    # Keyboard
    ##########

    def type_key(self, text: str, interval: int = 0) -> None:
        """
        Type a text char by char (individual key events).

        Args:
            text (str): text to be typed.
            interval (int, optional): interval (ms) between each key press. Defaults to 0

        """
        self.kb_type(text=text, interval=interval)

    def kb_type(self, text: str, interval: int = 0) -> None:
        """
        Type a text char by char (individual key events).

        Args:
            text (str): text to be typed.
            interval (int, optional): interval (ms) between each key press. Defaults to 0

        """
        for char in text:
            self._kb_controller.type(char)
            self.sleep(interval)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def paste(self, text: Optional[str] = None, wait: int = 0) -> None:
        """
        Paste content from the clipboard.

        Args:
            text (str, optional): The text to be pasted. Defaults to None
            wait (int, optional): Wait interval (ms) after task
        """
        if text:
            pyperclip.copy(text)
        self.control_v()
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def copy_to_clipboard(self, text: str, wait: int = 0) -> None:
        """
        Copy content to the clipboard.

        Args:
            text (str): The text to be copied.
            wait (int, optional): Wait interval (ms) after task
        """
        pyperclip.copy(text)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def tab(self, wait: int = 0, presses: int = 1) -> None:
        """
        Press key Tab

        Args:
            wait (int, optional): Wait interval (ms) after task
            presses (int): Number of times to press the key. Defaults to 1.

        """
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        for _ in range(presses):
            self._kb_controller.tap(Key.tab)
            self.sleep(delay)

    def enter(self, wait: int = 0, presses: int = 1) -> None:
        """
        Press key Enter

        Args:
            wait (int, optional): Wait interval (ms) after task
            presses (int): Number of times to press the key. Defaults to 1.

        """
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        for _ in range(presses):
            self._kb_controller.tap(Key.enter)
            self.sleep(delay)

    def key_right(self, wait: int = 0) -> None:
        """
        Press key Right

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.right)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_enter(self, wait: int = 0) -> None:
        """
        Press key Enter

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.enter(wait)

    def key_end(self, wait: int = 0) -> None:
        """
        Press key End

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.end)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_esc(self, wait: int = 0) -> None:
        """
        Press key Esc

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.esc)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def _key_fx(self, idx: KeyCode, wait: int = 0) -> None:
        """
        Press key F[idx] where idx is a value from 1 to 12

        Args:
            idx (str): F key index from 1 to 12
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(idx)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def key_f1(self, wait: int = 0) -> None:
        self._key_fx(Key.f1, wait=wait)

    def key_f2(self, wait: int = 0) -> None:
        self._key_fx(Key.f2, wait=wait)

    def key_f3(self, wait: int = 0) -> None:
        self._key_fx(Key.f3, wait=wait)

    def key_f4(self, wait: int = 0) -> None:
        self._key_fx(Key.f4, wait=wait)

    def key_f5(self, wait: int = 0) -> None:
        self._key_fx(Key.f5, wait=wait)

    def key_f6(self, wait: int = 0) -> None:
        self._key_fx(Key.f6, wait=wait)

    def key_f7(self, wait: int = 0) -> None:
        self._key_fx(Key.f7, wait=wait)

    def key_f8(self, wait: int = 0) -> None:
        self._key_fx(Key.f8, wait=wait)

    def key_f9(self, wait: int = 0) -> None:
        self._key_fx(Key.f9, wait=wait)

    def key_f10(self, wait: int = 0) -> None:
        self._key_fx(Key.f10, wait=wait)

    def key_f11(self, wait: int = 0) -> None:
        self._key_fx(Key.f11, wait=wait)

    def key_f12(self, wait: int = 0) -> None:
        self._key_fx(Key.f12, wait=wait)

    def hold_shift(self, wait: int = 0) -> None:
        """
        Hold key Shift

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.press(Key.shift)
        self.sleep(wait)

    def release_shift(self) -> None:
        """
        Release key Shift.
        This method needs to be invoked after holding Shift or similar.
        """
        self._kb_controller.release(Key.shift)
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def alt_space(self, wait: int = 0) -> None:
        """
        Press keys Alt+Space

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap(Key.space)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def maximize_window(self) -> None:
        """
        Shortcut to maximize window on Windows OS.
        """
        with self._kb_controller.pressed(Key.alt, Key.space):
            self._kb_controller.tap("x")
        self.sleep(config.DEFAULT_SLEEP_AFTER_ACTION)

    def type_keys_with_interval(self, interval: int, keys: List) -> None:
        """
        Press a sequence of keys. Hold the keys in the specific order and releases them.

        Args:
            interval (int): Interval (ms) in which to press and release keys
            keys (list): List of keys to be pressed
        """
        formatted_keys = []
        for key in keys:
            if len(key) <= 1:
                formatted_keys.append(key)
                continue
            key = key.lower()
            key_value = keys_map.get(key, None)
            if key_value:
                formatted_keys.append(key_value)
            elif key in Key._member_names_:
                key_value = Key[key]
                formatted_keys.append(key_value)

        for key in formatted_keys:
            self._kb_controller.press(key)
            self.sleep(interval)
        for key in reversed(formatted_keys):
            self._kb_controller.release(key)
            self.sleep(interval)

    def type_keys(self, keys: List) -> None:
        """
        Press a sequence of keys. Hold the keys in the specific order and releases them.

        Args:
            keys (list): List of keys to be pressed
        """
        self.type_keys_with_interval(100, keys)

    def alt_e(self, wait: int = 0) -> None:
        """
        Press keys Alt+E

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap("e")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_r(self, wait: int = 0) -> None:
        """
        Press keys Alt+R

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap("r")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_f(self, wait: int = 0) -> None:
        """
        Press keys Alt+F

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap("f")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_u(self, wait: int = 0) -> None:
        """
        Press keys Alt+U

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap("u")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def alt_f4(self, wait: int = 0) -> None:
        """
        Press keys Alt+F4

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.alt):
            self._kb_controller.tap(Key.f4)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_c(self, wait: int = 0) -> str:
        """
        Press keys CTRL+C

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="c", wait=wait)
        return self.get_clipboard()

    def control_v(self, wait=0) -> None:
        """
        Press keys CTRL+V

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="v", wait=wait)

    def control_a(self, wait: int = 0) -> None:
        """
        Press keys CTRL+A

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="a", wait=wait)

    def control_f(self, wait: int = 0) -> None:
        """
        Press keys CTRL+F

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="f", wait=wait)

    def control_p(self, wait: int = 0) -> None:
        """
        Press keys CTRL+P

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="p", wait=wait)

    def control_u(self, wait: int = 0) -> None:
        """
        Press keys CTRL+U

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="u", wait=wait)

    def control_r(self, wait: int = 0) -> None:
        """
        Press keys CTRL+R

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="r", wait=wait)

    def control_t(self, wait: int = 0) -> None:
        """
        Press keys CTRL+T

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="t", wait=wait)

    def control_s(self, wait: int = 0) -> None:
        """
        Press keys CTRL+S

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="s", wait=wait)

    def control_key(self, key_to_press: Union[str, KeyCode], wait: int = 0) -> None:
        """
        Press CTRL and one more simple key to perform a keyboard shortcut

        Args:
            key_to_press (str): The key that will be pressed with the CTRL.
            wait (int, optional): Wait interval (ms) after task.

        """
        if isinstance(key_to_press, str):
            key_to_press = key_to_press.lower()

        key = Key.ctrl
        if platform.system() == "Darwin":
            key = Key.cmd
        with self._kb_controller.pressed(key):
            self._kb_controller.tap(key_to_press)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_end(self, wait: int = 0) -> None:
        """
        Press keys CTRL+End

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press=Key.end, wait=wait)

    def control_home(self, wait: int = 0) -> None:
        """
        Press keys CTRL+Home

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press=Key.home, wait=wait)

    def control_w(self, wait: int = 0) -> None:
        """
        Press keys CTRL+W

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self.control_key(key_to_press="w", wait=wait)

    def control_shift_p(self, wait: int = 0) -> None:
        """
        Press keys CTRL+Shift+P

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key_ctrl = Key.ctrl
        if platform.system() == "Darwin":
            key_ctrl = Key.cmd
        with self._kb_controller.pressed(key_ctrl, Key.shift):
            self._kb_controller.tap("p")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def control_shift_j(self, wait: int = 0) -> None:
        """
        Press keys CTRL+Shift+J

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        key_ctrl = Key.ctrl
        if platform.system() == "Darwin":
            key_ctrl = Key.cmd
        with self._kb_controller.pressed(key_ctrl, Key.shift):
            self._kb_controller.tap("j")
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def shift_tab(self, wait: int = 0) -> None:
        """
        Press keys Shift+Tab

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        with self._kb_controller.pressed(Key.shift):
            self._kb_controller.tap(Key.tab)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def get_clipboard(self) -> str:
        """
        Get the current content in the clipboard.

        Returns:
            text (str): Current clipboard content
        """
        return pyperclip.paste()

    def type_left(self, wait: int = 0) -> None:
        """
        Press Left key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.left)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_right(self, wait: int = 0) -> None:
        """
        Press Right key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.right)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_down(self, wait: int = 0) -> None:
        """
        Press Down key

        Args:
            wait (int, optional): Wait interval (ms) after task

        """
        self._kb_controller.tap(Key.down)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_up(self, wait: int = 0) -> None:
        """
        Press Up key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.up)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def type_windows(self, wait: int = 0) -> None:
        """
        Press Win logo key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.cmd)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def page_up(self, wait: int = 0) -> None:
        """
        Press Page Up key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.page_up)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def page_down(self, wait: int = 0) -> None:
        """
        Press Page Down key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.page_down)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def space(self, wait: int = 0) -> None:
        """
        Press Space key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.space)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def backspace(self, wait: int = 0) -> None:
        """
        Press Backspace key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.backspace)
        delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
        self.sleep(delay)

    def delete(self, wait: int = 0) -> None:
        """
        Press Delete key

        Args:
            wait (int, optional): Wait interval (ms) after task
        """
        self._kb_controller.tap(Key.delete)
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

    #############
    # Application
    #############

    @if_windows_os
    def connect_to_app(
        self, backend=Backend.WIN_32, timeout=60000, **connection_selectors
    ) -> "Application":
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
        self.app = connect(backend, timeout, **connection_selectors)
        return self.app

    @if_app_connected
    def find_app_window(self, waiting_time=10000, **selectors) -> "WindowSpecification":
        """
        Find a window of the currently connected application using the available selectors.

        Args:
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            **selectors: Attributes that can be used to filter an element.
                [See more details about the available selectors\
                ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/).

        Returns
            dialog (WindowSpecification): The window or control found.
        """
        dialog = find_window(self.app, waiting_time, **selectors)
        return dialog

    @if_app_connected
    def find_app_element(
        self,
        from_parent_window: "WindowSpecification" = None,
        waiting_time=10000,
        **selectors,
    ) -> "WindowSpecification":
        """
        Find a element of the currently connected application using the available selectors.
        You can pass the context window where the element is contained.

        Args:
            from_parent_window (WindowSpecification, optional): The element's parent window.
            waiting_time (int, optional): Maximum wait time (ms) to search for a hit.
                Defaults to 10000ms (10s).
            **selectors: Attributes that can be used to filter an element.
                [See more details about the available selectors\
                ](https://documentation.botcity.dev/frameworks/desktop/windows-apps/).

        Returns
            element (WindowSpecification): The element/control found.
        """
        element = find_element(self.app, from_parent_window, waiting_time, **selectors)
        return element
