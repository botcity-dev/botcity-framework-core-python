import sys
import pandas
import requests
import pyautogui
import keyboard
import botcity.core.config as cfg

# Speed up without sleep after action.
pyautogui.PAUSE = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.DARWIN_CATCH_UP_TIME = 0.01
cfg.DEFAULT_SLEEP_AFTER_ACTION = 0

# Add the resource images
add_image("start", "./resources/start.png")

# Download Input Spreadsheet
r = requests.get("http://www.rpachallenge.com/assets/downloadFiles/challenge.xlsx")

if r.status_code != 200:
    sys.exit('Error fetching the challenge spreadsheet.')

# Use Pandas to load the Excel Spreadsheet as a DataFrame:
df = pandas.read_excel(r.content)
df.dropna(axis='columns', inplace=True)

df.columns = df.columns.str.strip()

# Navigate to the website
browse("http://www.rpachallenge.com/")

# Find and click into the Start button
find("start")
click()

## Using Find one-by-one
for index, row in df.iterrows():
    # Click into main area of the page
    keyboard.send('command+a')
    keyboard.send('command+c')
    wait(20)
    content = get_clipboard()

    click_at(1000, 200)
    field_order = [x for x in content[content.rfind('!') + 1:].split('\n') if x in df.columns]

    for f in field_order:
        keyboard.send('tab')
        value = row[f]
        copy_to_clipboard(str(value))
        keyboard.send('command+v')
        wait(20)

    zkeyboard.send('enter')
    wait(50)
