import sys
import functools
import types
import inspect
from os import path

from botcity.core.base import State


class BaseBot:
    ...


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

    def action(self, execution=None):
        """
        Execute an automation action.

        Args:
            execution (BotExecution, optional): Information about the execution when running
                this bot in connection with the BotCity Maestro Orchestrator.
        """
        raise NotImplementedError("You must implement this method.")

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

    def get_resource_abspath(self, filename, resource_folder="resources"):
        """
        Compose the resource absolute path taking into account the package path.

        Args:
            filename (str): The filename under the resources folder.
            resource_folder (str, optional): The resource folder name. Defaults to `resources`.

        Returns:
            abs_path (str): The absolute path to the file.
        """
        return path.join(self._resources_path(resource_folder), filename)

    def _resources_path(self, resource_folder="resources"):
        path_to_class = sys.modules[self.__module__].__file__
        return path.join(path.dirname(path.realpath(path_to_class)), resource_folder)

    @classmethod
    def main(cls):
        try:
            from botcity.maestro import BotMaestroSDK, BotExecution
            maestro_available = True
        except ImportError:
            maestro_available = False

        bot = cls()
        execution = None
        # TODO: Refactor this later for proper parameters to be passed
        #       in a cleaner way
        if len(sys.argv) == 4:
            if maestro_available:
                server, task_id, token = sys.argv[1:4]
                bot.maestro = BotMaestroSDK(server=server)
                bot.maestro.access_token = token

                parameters = bot.maestro.get_task(task_id).parameters

                execution = BotExecution(server, task_id, token, parameters)
            else:
                raise RuntimeError("Your setup is missing the botcity-maestro-sdk package. "
                                   "Please install it with: pip install botcity-maestro-sdk")

        bot.action(execution)
