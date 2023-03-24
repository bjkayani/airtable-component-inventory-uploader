from selenium import webdriver
import time
import requests
from config import IMG_BB_API_KEY
from selenium.webdriver.common.by import By
import base64

# Downloading the image using Selenium
driver = webdriver.Chrome()
driver.get("https://www.digikey.com/en/products/detail/molex/2033900323/16920881")
time.sleep(2)
img = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[1]/div[1]/div[1]/div/div[1]/div/img")
src = img.get_attribute('src')
driver.quit()

# Saving the image to disk
with open("image.jpg", "wb") as f:
    f.write(requests.get(src).content)

# Uploading the image to free image hosting website

with open("image.jpg", "rb") as file:
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMG_BB_API_KEY,
        "image": base64.b64encode(file.read()),
    }
    res = requests.post(url, payload)

res = requests.post(url, payload)
res.raise_for_status()

# Printing out the public URL for that image
print(res.json()['data']['url_viewer'])