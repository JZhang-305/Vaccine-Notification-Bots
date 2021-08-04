import requests
import json
import time
import os
import re
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from urllib.request import urlopen as uReq
import tweepy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime


# input api key
api_key = ""
# input api secret key
api_secret_key = ""
# input access token
access_token = ""
# input access secret token
access_secret_token = ""


# put initials of the state
initials = ""

# put name of the state
state = ""

# put file_path to chromedriver
file_path = ""


options = webdriver.ChromeOptions()

# setup for chromedriver to run headless for less lag
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(file_path, options=options)

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_secret_token)
api = tweepy.API(auth)

# interval in seconds between each search
interval = 

# change cvs link if needed - link will not lead to correct 
cvslink = "https://www.cvs.com/immunizations/covid-19-vaccine?icid=coronavirus-lp-nav-vaccine"
cvslink2 = "http://bit.ly/cvsvaxbooker"

locations = {
    
}

# note: code below worked from Mar, 2020 - May, 2020 but does not anymore because of CVS website changes
driver.get(cvslink)
time.sleep(3)

link = driver.find_element_by_link_text(state)
link.click()
time.sleep(3)

cities = driver.find_elements_by_class_name("city")

counter = 0
for city in cities:
    locations[str(city.text)] = (counter, False)
    
    counter += 1


while True:

    driver.get(cvslink)
    time.sleep(7)
    link = driver.find_element_by_link_text(state)
    
    '''
    the try-except block below is to bypass CVS's pop-up message. 
    if clicking link to get state vaccine info fails because of click interference, I will close the pop-up
    '''

    try:
        link.click()
    except:
        survey = driver.find_element_by_link_text("No, thanks")
        survey.click()
        time.sleep(5)
        link.click()
        
    time.sleep(7)
    statuses = driver.find_elements_by_class_name("status")
   
    try:    
        for key in locations:

            # when specific cvs location has vaccine(s) but did not in the previous loop
            if "Available" in statuses[locations[key][0]].text and locations[key][1] == False:
                now = datetime.now()
                timestamp = now.strftime("%m/%d %H:%M")
                message = "As of " + timestamp + ": New appointment(s) available at [CVS - " + key + "]\n\n" + cvslink2
                
                # print message to console
                print(message)
                # tweeting message to vaccine bot account
                api.update_status(message)

                locations[key][1] = True
            
            # when specific cvs location still has vaccine(s) available
            elif "Available" in statuses[locations[key][0]].text and locations[key][1] == True:
                continue

            # when specific cvs location does not have vaccines
            else:
                locations[key][1] = False
                
                
                
    except:
        continue

    time.sleep(interval)
    
    
