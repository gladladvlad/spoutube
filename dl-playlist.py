#!/bin/python3

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import yt_dlp

#time.sleep(2)

link = "https://www.youtube.com/results?search_query={}".format("chris+hazelton+bambu")

webdriver_options = Options()
webdriver_options.add_argument("--headless")
webdriver_options.add_argument("--disable-crash-reporter")

driver = webdriver.Chrome(options=webdriver_options)
driver.implicitly_wait(0.5)
driver.get(link)

search_results = driver.find_elements(by=By.CSS_SELECTOR, value="a[id='video-title']")

for item in search_results:
    print("details: " + item.get_attribute("aria-label"))
    print("link: " + item.get_attribute("href"))

chosen = search_results[0].get_attribute('href')
ytdl_options = {'extract_audio': True, 'format': 'bestaudio', 'outtmpl': '%(title)s.mp3'}

ytdl = yt_dlp.YoutubeDL(ytdl_options)
ytdl.download(chosen)

driver.quit();
