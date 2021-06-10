import sys
import pandas
import requests
from botcity.core import DesktopBot


class Bot(DesktopBot):
    def action(self, execution=None):
        # Add the resource images
        self.add_image("First Name", self.get_resource_abspath("first_name.png"))
        self.add_image("Last Name", self.get_resource_abspath("last_name.png"))
        self.add_image("Company Name", self.get_resource_abspath("company_name.png"))
        self.add_image("Role in Company", self.get_resource_abspath("role.png"))
        self.add_image("Address", self.get_resource_abspath("address.png"))
        self.add_image("Email", self.get_resource_abspath("email.png"))
        self.add_image("Phone Number", self.get_resource_abspath("phone.png"))
        self.add_image("start", self.get_resource_abspath("start.png"))
        self.add_image("submit", self.get_resource_abspath("submit.png"))

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
        self.browse("http://www.rpachallenge.com/")

        # Find and click into the Start button
        self.find("start", waiting_time=50000)
        self.click()

        USE_FIND_MULTIPLE = True

        if USE_FIND_MULTIPLE:
            # Using Find Parallel
            for index, row in df.iterrows():
                results = self.find_multiple(labels, matching=0.8)
                for idx, (label, ele) in enumerate(results.items()):
                    if ele is None:
                        sys.exit(f'Could not find element for field: {label}')
                    x, y = ele.left, ele.top
                    if label == 'submit':
                        self.click_at(x + 10, y + 10)
                    else:
                        self.click_at(x + 10, y + 30)
                        self.copy_to_clipboard(str(row[df.columns[idx]]))
                        self.paste()
        else:
            # Using Find Serial Mode
            for index, row in df.iterrows():
                for col in df.columns:
                    entry_value = row[col]
                    self.find_text(col.strip(), matching=0.8)
                    self.click_relative(10, 30)
                    self.kb_type(str(entry_value))
                self.find("submit")
                self.click()
                self.wait(500)


if __name__ == '__main__':
    Bot.main()