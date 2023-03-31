from pyairtable import Table
from config import AIRTABLE_API_KEY
import yaml


def import_field_options():
    # API key saved in a config.py file
    table = Table(AIRTABLE_API_KEY, 'appFfYpN5r4tdGjZ0', 'Components')

    print('Updating field options yaml')

    table_list = table.all()
    category_list = []
    footprint_list = []

    for record in table_list:
        if 'Category' in record['fields']:
            category = record['fields']['Category']
            if category not in category_list:
                category_list.append(category)

        if 'Footprint' in record['fields']:
            footprint = record['fields']['Footprint']
            if footprint not in footprint_list:
                footprint_list.append(footprint)

    category_list.sort()
    footprint_list.sort()

    field_options_dict = {'footprint': footprint_list,
                    'category': category_list}

    with open('field_options.yaml', 'w') as file:
        yaml.dump(field_options_dict, file)
