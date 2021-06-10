<p align="center">
  <h1 align="center">BotCity Framework Core - Python</h1>

  <p align="center">
    <strong>« Explore Framework <a href="https://botcity-dev.github.io/botcity-framework-core-python/">docs</a> »</strong>
    <br>
    <br>
    <a href="https://github.com/botcity-dev/botcity-framework-core-python/issues/new?template=bug-report.md">Report bug</a>
    ·
    <a href="https://github.com/botcity-dev/botcity-framework-core-python/issues/new?template=feature-request.md&labels=request">Request feature</a>
    ·
    <a href="https://github.com/botcity-dev/botcity-framework-core-python/blob/main/.github/CONTRIBUTING.md">How to Contribute</a>
    ·
    <a href="https://github.com/botcity-dev/botcity-framework-core-python/blob/main/.github/SUPPORT.md">Support</a>
  </p>
</p>

<br>

# Prerequisites
* Python 3.7+
* pyautogui
* keyboard
* pyperclip
* opencv

Python package requirements are listed in the requirements.txt file, which can
be used to install all requirements from pip: 'pip install -r requirements.txt'

# Running the Tests
In order to run the tests you will need to install some dependencies that are
not part of the runtime dependencies.

Assuming that you have cloned this repository do:

```bash
pip install -r test-requirements.txt

python run_tests.py
```

# Running the Examples
There are various examples of the features and how to get started.
Check out the examples folder.

# Building the Documentation Locally
In order to build the documentation you will need to install some dependencies
that are not part of the runtime dependencies.

Assuming that you have cloned this repository do:

```bash
pip install -r docs-requirements.txt

mkdocs build
```

This will generate the HTML documentation in the `<>/site`
folder. Look for the `index.html` file and open it with your browser.

# Online Documentation

Documentation is available at https://botcity-dev.github.io/botcity-framework-core-python.
