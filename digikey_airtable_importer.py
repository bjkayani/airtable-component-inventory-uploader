from pyairtable import Table
from bom_processor import get_processed_digikey_bom
import os
from termcolor import colored
from config import AIRTABLE_API_KEY

# API key saved in a config.py file
table = Table(AIRTABLE_API_KEY, 'appFfYpN5r4tdGjZ0', 'Components')

entry = {
    "Part Number": "",
    "Quantity": 0,
    "Footprint": "",
    "Product Page Link": "",
    "Image": [{"url": ""}],
    "Distributor Part Number": "",
    "Product Page Link": "",
    "Description": "",
    "Value": "",
    "Datasheet Link": "",
    "Category": ""
}

def get_csv_bom_file():
    current_dir = os.getcwd() + "/bom"
    files = os.listdir(current_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    if csv_files:
        print(colored('CSV files in the current directory:', 'green'))
        for i, f in enumerate(csv_files):
            print(colored(f'{i}: {f}', 'yellow'))
    while True:
        if csv_files:
            choice = input('Enter the number of the CSV file you want to load or enter the path to your own CSV file: ')
        else:
            choice = input('Enter the path to your own CSV file: ')
        if choice.isdigit() and int(choice) < len(csv_files):
            return os.path.join(current_dir, csv_files[int(choice)])
        elif os.path.exists(choice) and choice.endswith('.csv'):
            return choice
        else:
            print(colored('Invalid choice. Please try again.', 'red'))

print(colored('---------- Digikey BOM Airtable Importer ----------', 'red'))

bom_path = get_csv_bom_file()

bom = get_processed_digikey_bom(bom_path)

for index, row in bom.iterrows():
    # These parameters come directly from the BOM loaded
    entry["Part Number"] = bom.loc[index, 'Manufacturer Part Number']
    entry["Distributor Part Number"] = bom.loc[index, 'Part Number']
    entry["Quantity"] = int(bom.loc[index, 'Quantity'])
    entry["Description"] = bom.loc[index, 'Description']

    # Footprint from loaded BOM is matched to predefined list
    if bom.loc[index, 'Footprint'] is None or bom.isna().loc[index, 'Footprint']:
        entry.pop("Footprint", None)
    else:
        entry["Footprint"] = bom.loc[index, 'Footprint']

    # These parameters are scrapped from the product page using selenium
    entry["Product Page Link"] = bom.loc[index, 'Web Link']
    entry["Datasheet Link"] = bom.loc[index, 'Datasheet']
    entry["Category"] = bom.loc[index, 'Category']

    # entry["Image"][0]["url"] = bom.loc[index, 'Image']

    entry["Image"][0]["url"] = bom.loc[index, 'Image']
    
    # Remove any parameter that doesnt have information
    for key in list(entry.keys()):
        if entry[key] == 'None' or entry[key] == '':
            entry.pop(key)
    
    print(entry)

    table.create(entry)
