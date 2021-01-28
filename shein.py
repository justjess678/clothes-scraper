#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 13:43:50 2020

@author: jess
"""
import collections
import csv
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


features = open("features.txt").readlines()

options = webdriver.ChromeOptions()
prefs = {'profile.default_content_setting_values': {'images': 2, 'javascript': 2}}
options.add_argument("headless")
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome("./lib/chromedriver", options=options)


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}\n".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    

def fill_dict(url,v=False):
    #fill with page info
    item_dict = {}
    item_dict["url"] = url
    driver.get(url)
    
    # gets around coupon popup; Remove if not needed
    try:
        button = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div/div/i')
        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(button).click(button).perform()
    except Exception as e:
        pass
    # end coupon workaround
    item_dict["Name"] = None
    try:
        item_dict["Name"] = driver.find_element_by_xpath('//div[@class="product-intro__head-name"]').text
        print("Product: ", item_dict["Name"])
    except Exception as e:
        pass
    try:
        colours = driver.find_elements_by_xpath('//div[@class="color-name"]')
    except Exception as e:
        print(e)
        
    col_list = []
    for col in colours:
        col_list.append(col.text)
    item_dict["Color"] = col_list
    
    try:
        driver.find_element_by_xpath('//div[@class="product-intro__description-head"]').click()
    
        desc = driver.find_elements_by_xpath('//div[@class="product-intro__description-table-item"]')
        for d in desc:
            k = d.find_element_by_xpath('.//div[@class="key"]').text[:-1]
            v = d.find_element_by_xpath('.//div[@class="val"]').text
            if 'Color' in k and item_dict["Color"]==[]:
                item_dict["Color"] = v
            else:
                if ',' in v:
                    item_dict[k] = v.split(',')
                elif '/' in v:
                    item_dict[k] = v.split('/')
                else:
                    item_dict[k] = v
    except Exception as e:
        print(e)

    try:
        item_dict["Image"] = driver.find_element_by_xpath('//div[@class="product-intro__main"]//img').get_attribute("src")
    except Exception as e:
        print(e)
    
    try:
        if 'Tops' in driver.find_element_by_xpath('//div[@class="bread-crumb__inner"]').text:
            item_dict["Type"] = "Top"
        elif 'Bottom' in driver.find_element_by_xpath('//div[@class="bread-crumb__inner"]').text:
            item_dict["Type"] = "Bottom"
        elif 'Dresses' in driver.find_element_by_xpath('//div[@class="bread-crumb__inner"]').text:
            item_dict["Type"] = "Dress"
    except Exception as e:
        print(e)
        
    try:
        if 'Women' in driver.find_element_by_xpath('//div[@class="bread-crumb__inner"]').text:
            item_dict["Gender"] = "F"
        else:
            item_dict["Gender"] = "M"
    except Exception as e:
        print(e)
        
        
    return item_dict
    
def get_links(list_url):
    driver.get(list_url)    
    
    next_page = 1
    links= []
    
    while next_page is not None:
        
        #read links
        item_links = driver.find_elements_by_xpath('//div[@class="S-product-item__info"]/a')

        
        if len(item_links) == 0:
            next_page = None
            print("No more pages in this category")
        else:
            next_page+=1
            for il in item_links:
                links.append(il.get_attribute("href"))
                
            driver.get(list_url +"?page="+str(next_page))
    
    return links


links = []

pages = ["https://www.shein.com/Bottoms-c-1767.html",
         "https://www.shein.com/Tops-c-1766.html",
         "https://www.shein.com/women-dresses-c-1727.html"
         ]

for page in pages:
    print("Getting links for:", page)
    links.append(get_links(page))
    
final_links = list(set([item for sublist in links for item in sublist]))
"""
final_links = ["https://www.shein.com/Zebra-Striped-Print-Seam-Front-Colorblock-Tee-p-2038746-cat-1738.html",
               "https://www.shein.com/Tropical-Print-Dress-p-2023211-cat-1727.html"]
"""

fields = []
print("Getting fieldnames...")
count = 0
all_dicts = []

for fl in final_links:
    count += 1
    try:
        tmp = fill_dict(fl, False)
        print(tmp)
        for key in tmp.keys():
            fields.append(key)
        all_dicts.append(tmp)
        update_progress(count/len(final_links))
    except Exception as e:
        pass
    
update_progress(0)
    
fieldnames = list(set(fields))

print("Writing CSV...")
    
with open('OUT.csv', mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    for ad in all_dicts:
        count += 1
        writer.writerow(ad)
        update_progress(count/len(all_dicts))

driver.close()