import sys
import pandas
import requests
from botcity.core import *
import botcity.config as cfg

# Speed up without sleep after action.
cfg.DEFAULT_SLEEP_AFTER_ACTION = 0

# Add the resource images
add_image("First Name", "./resources/first_name.png")
add_image("Last Name", "./resources/last_name.png")
add_image("Company Name", "./resources/company_name.png")
add_image("Role in Company", "./resources/role.png")
add_image("Address", "./resources/address.png")
add_image("Email", "./resources/email.png")
add_image("Phone Number", "./resources/phone.png")
add_image("start", "./resources/start.png")
add_image("submit", "resources/submit_large.png")

# Download Input Spreadsheet
r = requests.get("http://www.rpachallenge.com/assets/downloadFiles/challenge.xlsx")

if r.status_code != 200:
    sys.exit('Error fetching the challenge spreadsheet.')

# Use Pandas to load the Excel Spreadsheet as a DataFrame:
df = pandas.read_excel(r.content)
df.dropna(axis='columns', inplace=True)

# Create a list with the column names
labels = [c.strip() for c in df.columns]
labels.append("submit")

# Navigate to the website
browse("http://www.rpachallenge.com/")

# Find and click into the Start button
find("start")
click()

USE_FIND_MULTIPLE = True

if USE_FIND_MULTIPLE:
    ### Using Find Multiple
    for index, row in df.iterrows():
        results = find_multiple(labels, matching=0.8)
        for idx, (label, ele) in enumerate(results.items()):
            if ele is None:
                sys.exit(f'Could not find element for field: {label}')
            x, y = ele.left, ele.top
            if label == 'submit':
                click_at(x + 10, y + 10)
            else:
                click_at(x + 10, y + 30)
                copy_to_clipboard(str(row[df.columns[idx]]))
                paste()
else:
    ## Using Find one-by-one
    for index, row in df.iterrows():
        for col in df.columns:
            entry_value = row[col]
            find_text(col.strip(), matching=0.8)
            click_relative(10, 30)
            kb_type(str(entry_value))
        find("submit")
        click()
        wait(500)
