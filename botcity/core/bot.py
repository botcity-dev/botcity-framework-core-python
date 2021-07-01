import functools
import types
import inspect

from botcity.base import BaseBot
from botcity.base import State


class DesktopBot(BaseBot):
    """
    Base class for Desktop Bots.
    Users must implement the `action` method in their classes.

    Attributes:
        state (State): The internal state of this bot.
        maestro (BotMaestroSDK): an instance to interact with the BotMaestro server.

    """
    def __init__(self):
        self.state = State()
        self.maestro = None

        import botcity.core.display as display
        import botcity.core.browser as browser
        import botcity.core.mouse as mouse
        import botcity.core.keyboard as keyboard
        import botcity.core.misc as misc

        self.__import_commands(display)
        self.__import_commands(browser)
        self.__import_commands(mouse)
        self.__import_commands(keyboard)
        self.__import_commands(misc)

    def __import_commands(self, module):
        def wrapper(f):
            @functools.wraps(f)
            def wrap(*args, **kwargs):
                func_params = inspect.signature(f).parameters
                if 'state' in func_params:
                    kwargs['state'] = self.state
                if args[0] == self:
                    return f(*args[1:], **kwargs)
                return f(*args, **kwargs)
            return wrap

        deny_list = getattr(module, '__deny_list', [])
        methods = [m for m in dir(module) if not m.startswith('__') and m not in deny_list]
        for m in methods:
            func = module.__dict__[m]
            wrapped = wrapper(func)
            setattr(self, m, types.MethodType(wrapped, self))
