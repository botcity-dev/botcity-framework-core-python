# Module for OS Compatibility issues and PyAutoGui
import platform

import pyautogui

if platform.system() == "Darwin":
    import pyautogui._pyautogui_osx as osx

    def _multiClick(x, y, button, num, interval=0.0):
        import Quartz
        btn = None
        down = None
        up = None

        if button == osx.LEFT:
            btn = Quartz.kCGMouseButtonLeft
            down = Quartz.kCGEventLeftMouseDown
            up = Quartz.kCGEventLeftMouseUp
        elif button == osx.MIDDLE:
            btn = Quartz.kCGMouseButtonCenter
            down = Quartz.kCGEventOtherMouseDown
            up = Quartz.kCGEventOtherMouseUp
        elif button == osx.RIGHT:
            btn = Quartz.kCGMouseButtonRight
            down = Quartz.kCGEventRightMouseDown
            up = Quartz.kCGEventRightMouseUp
        else:
            assert False, "button argument not in ('left', 'middle', 'right')"

        mouseEvent = Quartz.CGEventCreateMouseEvent(None, down, (x, y), btn)
        Quartz.CGEventSetIntegerValueField(mouseEvent, Quartz.kCGMouseEventClickState, num)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouseEvent)
        Quartz.CGEventSetType(mouseEvent, up)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouseEvent)


def click(x=None, y=None, clicks=1, interval=0.0, button="left", **kwargs):
    """
    This method is here due to issues with pyautogui implementation of multiple clicks on macOS.
    For that, the code above from _multiClick was pulled from pyautogui and locally patched.
    A PR will be submitted to the pyautogui project to fix the issue upstream and once a new
    release with the patch is available we will remove our local patch here.
    """
    if platform.system() == "Darwin":
        _multiClick(x=x, y=y, button=button, num=clicks, interval=interval)
    else:
        pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button, **kwargs)
