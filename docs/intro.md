# Getting Started

After you installed this package, the next step is to
import the package into your code and start using the
functions to build your RPA pipeline.

```python
from botcity.core import *
```

As a demonstration of the library, let's build a simple
bot together that will open Google in your browser and
execute a seach.

## Opening the browser
To open the browser you can leverage the `browser` function
which takes as argument a URL.

```python
browser("https://www.google.com")
```

## Next Steps

Check our example and experiment with the API.
Let us know where it can be improved.