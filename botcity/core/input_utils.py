import platform
import time

from pynput.keyboard import Key
from pynput.mouse import Button, Controller

keys_map = {
    "num0": '0',
    "num1": '1',
    "num2": '2',
    "num3": '3',
    "num4": '4',
    "num5": '5',
    "num6": '6',
    "num7": '7',
    "num8": '8',
    "num9": '9',
    "add": '+',
    "decimal": ',',
    "subtract": '-',
    "multiply": '*',
    "divide": '/',
    "separator": '|',
    "altleft": Key.alt_l,
    "altright": Key.alt_r,
    "capslock": Key.caps_lock,
    "command": Key.cmd,
    "win": Key.cmd,
    "winleft": Key.cmd_l,
    "winright": Key.cmd_r,
    "ctrlleft": Key.ctrl_l,
    "ctrlright": Key.ctrl_r,
    "escape": Key.esc,
    "pagedown": Key.page_down,
    "pageup": Key.page_up,
    "pgdn": Key.page_down,
    "pgup": Key.page_up,
    "shiftleft": Key.shift_l,
    "shiftright": Key.shift_r,
    "playpause": Key.media_play_pause,
    "volumemute": Key.media_volume_mute,
    "volumedown": Key.media_volume_down,
    "volumeup": Key.media_volume_up,
    "prevtrack": Key.media_previous,
    "nexttrack": Key.media_next,
    "return": Key.enter
}

if platform.system() != "Darwin":
    keys_map.update(
        {
            "numlock": Key.num_lock,
            "prtsc":  Key.print_screen,
            "prtscr": Key.print_screen,
            "printscreen": Key.print_screen,
            "prntscrn": Key.print_screen,
            "print": Key.print_screen,
            "scrolllock": Key.scroll_lock,
        }
    )

mouse_map = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle
}


def _mouse_click(mouse_controller: Controller, x: int, y: int, clicks=1, interval_between_clicks=0, button='left'):
    """
    Moves the mouse and clicks at the coordinate defined by x and y.
    """
    if platform.system() == "Darwin":
        from . import os_compat
        os_compat.osx_click(x=x, y=y, clicks=clicks, interval=interval_between_clicks, button=button)
    else:
        mouse_button = mouse_map.get(button, None)
        if not mouse_button:
            raise ValueError(f'''Invalid mouse button name.
            The mouse button has to be one of these values: {list(mouse_map.keys())}''')

        mouse_controller.position = (x, y)
        time.sleep(0.1)
        for i in range(clicks):
            mouse_controller.click(button=mouse_button, count=1)
            time.sleep(interval_between_clicks / 1000.0)
