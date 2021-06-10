# Getting Started

After you installed this package, the next step is to
import the package into your code and start using the
functions to build your RPA pipeline.

```python
from botcity.core import *
```

As a demonstration of the library, let's build a simple
bot together that will open BotCity's website in your browser.

## Opening the browser
To open the browser you can leverage the `browser` function
which takes as argument a URL.

```python
browser("https://www.botcity.dev/en")
```

You can use this framework in two ways:

- Scripting using the functions
- Creating a Bot class

The second method is the best if you plan to integrate your bot with the BotCity Maestro SDK.
The template project uses the Bot class and the examples cover both approaches.

## Template Project

We created a template project using Cookiecutter to help
you create new bots using BotCity's Python Framework.

Take a look into the [template project website](https://github.com/botcity-dev/bot-python-template) for more information
on how to use it and get started.

## Next Steps

Check our examples and experiment with the API.
Let us know where it can be improved.

Have fun automating!