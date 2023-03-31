import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import os
from constants import category_list
from constants import footprint_list
from config import IMG_BB_API_KEY
import requests
import base64
import string

lcsc_drop_column_list = ['Customer NO.', 'RoHS', 'Min\Mult Order Qty.', 'Order Price', 'Product Link', 'Customer #', 'Customer NO.', 'Product Link']

digikey_drop_column_list = ['Index', 'Description', 'Customer Reference', 'Extended Price']

def find_category(category_text):
    for cat in category_list:
        cat_split = cat.split(" ")
        for cat_split_element in cat_split:
            if cat_split_element in category_text:
                return cat
    # print('Category not found!')       
    return


# TODO: Deal with SOP Package
def find_footprint(footprint_text):
    for fp in footprint_list:
        fp_split = fp.split(" ")
        for fp_split_element in fp_split:
            if fp_split_element in footprint_text:
                return fp
    # print('Footprint not found!')       
    return

def load_lcsc_bom(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    # Required LCSC BOM columns
    required_columns = ['LCSC Part Number', 'Manufacture Part Number', 'Package', 'Description','Order Qty.','Unit Price']

    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Check if the required columns are present
    if not set(required_columns).issubset(set(df.columns)):
        print(f"File {file_path} does not contain all required columns.")
        return None

    return df

def load_digikey_bom(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    # Required Digikey BOM columns
    required_columns = ['Part Number', 'Manufacturer Part Number','Quantity','Unit Price']

    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Check if the required columns are present
    if not set(required_columns).issubset(set(df.columns)):
        print(f"File {file_path} does not contain all required columns.")
        return None
    
    # Remove empty rows
    df = df.dropna(subset=[df.columns[0]])

    return df

def get_processed_digikey_bom(bom_path):

    digikey_bom = load_digikey_bom(bom_path)

    # Remove unwanted columns
    for column in digikey_drop_column_list:
        if column in digikey_bom.columns:
            digikey_bom.drop(column, axis=1, inplace=True)

    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.digikey.com")
    time.sleep(2)

    # Add new columns
    digikey_bom['Category'] = list(range(len(digikey_bom)))  
    digikey_bom['Description'] = list(range(len(digikey_bom)))  
    digikey_bom['Web Link'] = list(range(len(digikey_bom)))   
    digikey_bom['Image'] = list(range(len(digikey_bom)))      
    digikey_bom['Datasheet'] = list(range(len(digikey_bom)))  
    digikey_bom['Footprint'] = list(range(len(digikey_bom))) 

    for index, row in digikey_bom.iterrows():
        print(f" \nProcessing component: {digikey_bom.loc[index, 'Manufacturer Part Number']}")

        # Enter the part number in the search field
        try:
            search_field = driver.find_element(By.XPATH, "/html/body/header/div[1]/div[1]/div/div[2]/div[2]/input")
            search_field.send_keys(digikey_bom.loc[index, 'Part Number'])
            search_field.send_keys(Keys.ENTER)
        except Exception as e:
            print(e)
            break

        # Allow the page to load
        time.sleep(2)
        digikey_bom.loc[index, 'Web Link'] = driver.current_url

        # Get category and find the closest match from specified list
        try:
            category_element = driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[1]/div[1]/div[3]/div/table/tbody/tr[1]/td[2]/div/div[1]/a") 
            category_text = category_element.text
            category_match = find_category(category_text)
            digikey_bom.loc[index, 'Category'] = str(category_match)
            print(f'Category text: {category_text}  Category match: {category_match}')
        except Exception as e:
            digikey_bom.loc[index, 'Category'] = "None"
            print("Cant get Category")

        image_xpaths = ['/html/body/div[3]/main/div/div[1]/div[1]/div[1]/div/div[1]/div/img',
                        '/html/body/div[3]/main/div/div[1]/div[1]/div[1]/div/div[3]/div/div[2]/div/img']

        # Get url of the image
        try:
            for xpath in image_xpaths:
                try:
                    image_element = driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    pass
            image_url = image_element.get_attribute("src")
            print(f'Image URL: {image_url}')
        except Exception as e:
            digikey_bom.loc[index, 'Image'] = 'None'
            print('Cant get Image URL')

        # Save the image
        image_name = digikey_bom.loc[index, 'Manufacturer Part Number'] + ".jpg"
        image_name = image_name.replace("/", "-")
        print(image_name)
        with open("images/" + image_name, "wb") as f:
            f.write(requests.get(image_url).content)

        # Upload the image to ImgBB
        try:
            with open("images/" + image_name, "rb") as file:
                url = "https://api.imgbb.com/1/upload"
                payload = {
                    "key": IMG_BB_API_KEY,
                    "image": base64.b64encode(file.read()),
                }
                res = requests.post(url, payload)
            res = requests.post(url, payload)
            res.raise_for_status()
            digikey_bom.loc[index, 'Image'] = res.json()['data']['url']
            print(f"ImgBB URL: {res.json()['data']['url']}")
        except Exception as e:
            digikey_bom.loc[index, 'Image'] = 'None'
            print('Cant upload image')

        datasheet_xpaths = ['/html/body/div[3]/main/div/div[1]/div[1]/div[2]/div/table/tbody/tr[8]/td[2]/a',
                            '/html/body/div[3]/main/div/div[1]/div[1]/div[2]/div/table/tbody/tr[7]/td[2]/a']
        
        # Get the url of the datasheet
        try:
            for xpath in datasheet_xpaths:
                try:
                    datasheet_element = driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    pass
            datasheet_url = datasheet_element.get_attribute("href")
            digikey_bom.loc[index, 'Datasheet'] = str(datasheet_url)
            print(f'Datasheet URL: {datasheet_url}')
        except Exception as e:
            digikey_bom.loc[index, 'Datasheet'] = 'None'
            print("Cant get Datasheet URL")


        # Get the detailed description

        description_xpaths = ['/html/body/div[3]/main/div/div[1]/div[1]/div[2]/div/table/tbody/tr[6]/td[2]/div',
                              '/html/body/div[3]/main/div/div[1]/div[1]/div[2]/div/table/tbody/tr[5]/td[2]/div']
        
        try:
            for xpath in description_xpaths:
                try:
                    description_element = driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    pass
            description_text = description_element.text
            digikey_bom.loc[index, 'Description'] = str(description_text)
            print(f'Description: {description_text}')
        except Exception as e:
            digikey_bom.loc[index, 'Description'] = 'None'
            print("Cant get description")

        # Get the footprint match using the description text
        footprint_match = find_footprint(description_text)
        digikey_bom.loc[index, 'Footprint'] = footprint_match
        print(f'Footprint: {footprint_match}')

        driver.get("https://www.digikey.com")
        time.sleep(2)
        
    driver.quit()

    # Generate a timestamped filename
    filename = f'Digikey_BOM_{time.strftime("%Y%m%d-%H%M%S")}.csv'
    
    # Save the DataFrame to a CSV file
    digikey_bom.to_csv("bom/" + filename, index=False)

    return digikey_bom

# TODO: Replace any hard coded indexes
def get_processed_lcsc_bom(bom_path):

    lcsc_bom = load_lcsc_bom(bom_path)

    # Remove unwanted columns
    for column in lcsc_drop_column_list:
        if column in lcsc_bom.columns:
            lcsc_bom.drop(column, axis=1, inplace=True)

    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.lcsc.com")

    # Allow the page to load and dismiss popup
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div[3]/div/div/div[3]/button[1]/span")))
    button.click()
    time.sleep(2)

    # Add new columns
    lcsc_bom['Category'] = list(range(len(lcsc_bom)))   
    lcsc_bom['Web Link'] = list(range(len(lcsc_bom)))   
    lcsc_bom['Image'] = list(range(len(lcsc_bom)))      
    lcsc_bom['Datasheet'] = list(range(len(lcsc_bom)))  

    lcsc_bom.rename(columns={'Manufacture Part Number': 'Manufacturer Part Number'}, inplace=True)

    for index, row in lcsc_bom.iterrows():

        print(f" \nProcessing component: {lcsc_bom.loc[index, 'Manufacturer Part Number']}")

        # Enter the part number in the search field
        try:
            search_field = driver.find_element(By.XPATH, "//*[@id='input-23']")
            search_field.send_keys(row[0])
            search_field.send_keys(Keys.ENTER)
        except Exception as e:
            print(e)
            break

        # Allow the page to load
        time.sleep(2)
        lcsc_bom.loc[index, 'Web Link'] = driver.current_url

        # Get category and find the closest match from specified list
        try:
            category_element = driver.find_element(By.XPATH, "//*[@id='app']/div[1]/main/div/div/div[2]/div/div/div[1]/div[3]/table/tbody/tr[1]/td[2]/a") 
            category_text = category_element.text
            category_match = find_category(category_text)
            lcsc_bom.loc[index, 'Category'] = str(category_match)
            print(f'Category text: {category_text}  Category match: {category_match}')
        except Exception as e:
            lcsc_bom.loc[index, 'Category'] = "None"
            print("Cant get Category")

        image_xpaths = ["//*[@id='app']/div/main/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/div[1]/img"]

        # Get url of the image
        try:
            for xpath in image_xpaths:
                try:
                    image_element = driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    pass
            image_url = image_element.get_attribute("src")
            print(f'Image URL: {image_url}')
        except Exception as e:
            lcsc_bom.loc[index, 'Image'] = 'None'
            print('Cant get Image URL')

        # Save the image
        try:
            image_name = lcsc_bom.loc[index, 'Manufacturer Part Number'] + ".jpg"
            image_name = image_name.replace("*", "-")
            with open("images/" + image_name, "wb") as f:
                f.write(requests.get(image_url).content)
        except Exception as e:
            print('Cant download image')

        # Upload the image to ImgBB
        try:
            with open("images/" + image_name, "rb") as file:
                url = "https://api.imgbb.com/1/upload"
                payload = {
                    "key": IMG_BB_API_KEY,
                    "image": base64.b64encode(file.read()),
                }
                res = requests.post(url, payload)
            res = requests.post(url, payload)
            res.raise_for_status()
            lcsc_bom.loc[index, 'Image'] = res.json()['data']['url']
            print(f"ImgBB URL: {res.json()['data']['url']}")
        except Exception as e:
            lcsc_bom.loc[index, 'Image'] = 'None'
            print('Cant upload image')


        # Get the url of the datasheet
        try:
            datasheet_element = driver.find_element(By.XPATH, "//*[@id='app']/div[1]/main/div/div/div[2]/div/div/div[1]/div[1]/div[2]/table/tbody/tr[6]/td[2]/a")
            datasheet_url = datasheet_element.get_attribute("href")
            lcsc_bom.loc[index, 'Datasheet'] = str(datasheet_url)
            print(f'Datasheet URL: {datasheet_url}')
        except Exception as e:
            lcsc_bom.loc[index, 'Datasheet'] = 'None'
            print("Cant get Datasheet URL")

        # Find closest match to inventory footprint and replace
        closest_match = find_footprint(lcsc_bom.loc[index, 'Package'])
        if closest_match:
            lcsc_bom.loc[index, 'Package'] = closest_match
            print(f"Footprint: {lcsc_bom.loc[index, 'Package']}")
        else:
            print(f"Footprint not found: {lcsc_bom.loc[index, 'Package']}")
            lcsc_bom.loc[index, 'Package'] = ''

        # Clear the search field
        search_field.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        time.sleep(1)

    driver.quit()

    # Generate a timestamped filename
    filename = f'LCSC_BOM_{time.strftime("%Y%m%d-%H%M%S")}.csv'
    
    # Save the DataFrame to a CSV file
    lcsc_bom.to_csv("bom/" + filename, index=False)

    return lcsc_bom


if __name__ == "__main__":
    bom_path = "2023-03-22T052753.csv"
    get_processed_digikey_bom(bom_path)
