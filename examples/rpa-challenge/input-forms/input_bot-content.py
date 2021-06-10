import botcity.core.config as cfg

import os
import sys
import pandas
import requests
from botcity.core import DesktopBot

# Speed up without sleep after action.
cfg.DEFAULT_SLEEP_AFTER_ACTION = 20


class Bot(DesktopBot):
    def action(self, execution):
        # Add the resource images
        self.add_image("start", self.get_resource_abspath("start.png"))

        # Download Input Spreadsheet
        r = requests.get("http://www.rpachallenge.com/assets/downloadFiles/challenge.xlsx")

        if r.status_code != 200:
            sys.exit('Error fetching the challenge spreadsheet.')

        # Use Pandas to load the Excel Spreadsheet as a DataFrame:
        df = pandas.read_excel(r.content)
        df.dropna(axis='columns', inplace=True)

        df.columns = df.columns.str.strip()

        # Navigate to the website
        self.browse("http://www.rpachallenge.com/")

        # Find and click into the Start button
        self.find("start")
        self.click()

        for index, row in df.iterrows():
            # Click into main area of the page
            self.control_a()
            self.control_c()
            content = self.get_clipboard()

            self.click_at(1000, 200)
            field_order = [x for x in content[content.rfind('!') + 1:].split(os.linesep) if x in df.columns]

            for f in field_order:
                self.tab()
                value = row[f]
                self.copy_to_clipboard(str(value))
                self.control_v()

            self.enter()


if __name__ == '__main__':
    Bot.main()