# Framework

The `botcity.core` module contains specialized implementations aimed at Desktop automation
such as `DesktopBot` which is described below.

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

::: botcity.core.bot.DesktopBot