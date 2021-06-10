import functools
import keyboard as kb
import pyperclip
import platform
from . import config
from .misc import sleep


def kb_type(text, interval=0):
    """
    Type a text char by char (individual key events).

    Args:
        text (str): text to be typed.
        interval (int, optional): interval (ms) between each key press. Defaults to 0

    """
    kb.write(text, delay=interval / 1000.0)
    sleep(config.DEFAULT_SLEEP_AFTER_ACTION)


def paste(text=None, wait=0):
    """
    Paste content from the clipboard.

    Args:
        text (str, optional): The text to be pasted. Defaults to None
        wait (int, optional): Wait interval (ms) after task
    """
    if text:
        pyperclip.copy(text)
        sleep(500)
    control_v()
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def copy_to_clipboard(text, wait=0):
    """
    Copy content to the clipboard.

    Args:
        text (str): The text to be copied.
        wait (int, optional): Wait interval (ms) after task
    """
    pyperclip.copy(text)
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def tab(wait=0):
    """
    Press key Tab

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('tab')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def enter(wait=0):
    """
    Press key Enter

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('enter')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def key_right(wait=0):
    """
    Press key Right

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('right')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def key_enter(wait=0):
    """
    Press key Right

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    enter(wait)


def key_end(wait=0):
    """
    Press key End

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('end')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def key_esc(wait=0):
    """
    Press key Esc

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('esc')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def _key_fx(idx, wait=0):
    """
    Press key Fidx where idx is a value from 1 to 12

    Args:
        idx (int): F key index from 1 to 12
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send(f'F{idx}')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def hold_shift(wait=0):
    """
    Hold key Shift

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.press('shift')
    sleep(wait)


def release_shift():
    """
    Release key Shift.
    This method needs to be invoked after holding Shift or similar.
    """
    kb.release('shift')


def alt_space(wait=0):
    """
    Press keys Alt+Space

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+space')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def maximize_window():
    """
    Shortcut to maximize window on Windows OS.
    """
    alt_space()
    sleep(1000)
    kb.send('x')


def type_keys_with_interval(interval, keys):
    """
    Press a sequence of keys. Hold the keys in the specific order and releases them.

    Args:
        interval (int): Interval (ms) in which to press and release keys
        keys (list): List of keys to be pressed
    """
    for k in keys:
        kb.press(k)
        sleep(interval)

    for k in keys.reverse():
        kb.release(k)
        sleep(interval)


def type_keys(keys):
    """
    Press a sequence of keys. Hold the keys in the specific order and releases them.

    Args:
        keys (list): List of keys to be pressed
    """
    type_keys_with_interval(100, keys)


def alt_e(wait=0):
    """
    Press keys Alt+E

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+e')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def alt_r(wait=0):
    """
    Press keys Alt+R

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+r')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def alt_f(wait=0):
    """
    Press keys Alt+F

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+f')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def alt_u(wait=0):
    """
    Press keys Alt+U

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+u')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def alt_f4(wait=0):
    """
    Press keys Alt+F4

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('alt+f4')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_c(wait=0):
    """
    Press keys CTRL+C

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+c')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_v(wait=0):
    """
    Press keys CTRL+V

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+v')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_a(wait=0):
    """
    Press keys CTRL+A

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+a')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_f(wait=0):
    """
    Press keys CTRL+F

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+f')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_p(wait=0):
    """
    Press keys CTRL+P

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+p')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_u(wait=0):
    """
    Press keys CTRL+U

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+u')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_r(wait=0):
    """
    Press keys CTRL+R

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+r')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_t(wait=0):
    """
    Press keys CTRL+T

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+t')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_end(wait=0):
    """
    Press keys CTRL+End

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+end')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_home(wait=0):
    """
    Press keys CTRL+Home

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+home')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_w(wait=0):
    """
    Press keys CTRL+W

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+w')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_shift_p(wait=0):
    """
    Press keys CTRL+Shift+P

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+shift+p')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def control_shift_j(wait=0):
    """
    Press keys CTRL+Shift+J

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    key = 'ctrl'
    if platform.system() == 'Darwin':
        key = 'command'
    kb.send(f'{key}+shift+j')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def shift_tab(wait=0):
    """
    Press keys Shift+Tab

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('shift+tab')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def get_clipboard():
    """
    Get the current content in the clipboard.

    Returns:
        text (str): Current clipboard content
    """
    return pyperclip.paste()


def type_left(wait=0):
    """
    Press Left key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('left')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def type_right(wait=0):
    """
    Press Right key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('right')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def type_down(wait=0):
    """
    Press Down key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('down')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def type_up(wait=0):
    """
    Press Up key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('up')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def type_windows(wait=0):
    """
    Press Win logo key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('windows')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def space(wait=0):
    """
    Press Space key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('space')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def backspace(wait=0):
    """
    Press Backspace key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('backspace')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


def delete(wait=0):
    """
    Press Delete key

    Args:
        wait (int, optional): Wait interval (ms) after task

    """
    kb.send('del')
    delay = max(0, wait or config.DEFAULT_SLEEP_AFTER_ACTION)
    sleep(delay)


type_key = kb_type

key_f1 = functools.partial(_key_fx, 1)
key_f2 = functools.partial(_key_fx, 2)
key_f3 = functools.partial(_key_fx, 3)
key_f4 = functools.partial(_key_fx, 4)
key_f5 = functools.partial(_key_fx, 5)
key_f6 = functools.partial(_key_fx, 6)
key_f7 = functools.partial(_key_fx, 7)
key_f8 = functools.partial(_key_fx, 8)
key_f9 = functools.partial(_key_fx, 9)
key_f10 = functools.partial(_key_fx, 10)
key_f11 = functools.partial(_key_fx, 11)
key_f12 = functools.partial(_key_fx, 12)

# Java API compatibility
typeWaitAfterChars = kb_type
copyToClipboard = copy_to_clipboard
keyRight = key_right
keyEnter = key_enter
keyEnd = key_end
keyEsc = key_esc
keyF1 = key_f1
keyF2 = key_f2
keyF3 = key_f3
keyF4 = key_f4
keyF5 = key_f5
keyF6 = key_f6
keyF7 = key_f7
keyF8 = key_f8
keyF9 = key_f9
keyF10 = key_f10
keyF11 = key_f11
keyF12 = key_f12
holdShift = hold_shift
releaseShift = release_shift
altSpace = alt_space
maximizeWindow = maximize_window
typeKeys = type_keys
typeKeysWithInterval = type_keys_with_interval
altE = alt_e
altR = alt_r
altF = alt_f
altU = alt_u
altF4 = alt_f4
controlC = control_c
controlV = control_v
controlA = control_a
controlF = control_f
controlP = control_p
controlU = control_u
controlR = control_r
controlT = control_t
controlEnd = control_end
controlHome = control_home
controlW = control_w
controlShiftP = control_shift_p
controlShiftJ = control_shift_j
ShiftTab = shift_tab
getClipboard = get_clipboard
typeLeft = type_left
typeRight = type_right
typeDown = type_down
typeUp = type_up
typeWindows = type_windows
typeKey = type_key
