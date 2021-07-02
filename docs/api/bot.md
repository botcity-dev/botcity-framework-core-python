# Bot API

This module contains specialized implementations aimed at Desktop automation such as `DesktopBot`
which is described below.

You are expected to implement the `action` method of the `DesktopBot` class in
your Bot class.

Here is a very brief example of a bot which opens the BotCity website:

```python
from botcity.core import DesktopBot


class Bot(DesktopBot):
    def action(self, execution):
        # Opens the BotCity website.
        self.browse("https://botcity.dev/en")


if __name__ == '__main__':
    Bot.main()
```


All functions from the API described below are accessible via the bot class as 
methods without the need to import any other module.

E.g.:

```python
class Bot(DesktopBot):
    def action(self, execution):
        # using browse from browser module
        self.browse(...)
        # using find from display module
        self.find(...)
        # using mouse_move from mouse module
        self.mouse_move(x=100, y=200)
        # using enter from keyboard module
        self.enter()

```

## DesktopBot API

::: botcity.core.bot.DesktopBot