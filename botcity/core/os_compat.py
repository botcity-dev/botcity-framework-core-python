# Module for OS Compatibility issues and PyAutoGui/pynput
import platform

OSX_LEFT = "left"
OSX_MIDDLE = "middle"
OSX_RIGHT = "right"


if platform.system() == "Darwin":
    def _multiClick(x, y, button, num, interval=0.0):
        import Quartz
        btn = None
        down = None
        up = None

        if button == OSX_LEFT:
            btn = Quartz.kCGMouseButtonLeft
            down = Quartz.kCGEventLeftMouseDown
            up = Quartz.kCGEventLeftMouseUp
        elif button == OSX_MIDDLE:
            btn = Quartz.kCGMouseButtonCenter
            down = Quartz.kCGEventOtherMouseDown
            up = Quartz.kCGEventOtherMouseUp
        elif button == OSX_RIGHT:
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


def osx_click(x=None, y=None, clicks=1, interval=0.0, button="left", **kwargs):
    """
    This method is here due to issues with pyautogui/pynput implementation of multiple clicks on macOS.
    For that, the code above from _multiClick was pulled from pyautogui and locally patched.
    """
    _multiClick(x=x, y=y, button=button, num=clicks, interval=interval)
