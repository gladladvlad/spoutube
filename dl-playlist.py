#!/bin/python3

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import yt_dlp

#time.sleep(2)

plist_file = open('spotify-playlists.json', 'r')
playlists = json.loads(plist_file.read())
plist_file.close()

for plist in playlists:
    print('---')
    print("\t" + plist['name'])
    print('---')

    for track in plist['tracks']:
        artist = track['artist']
        name = track['name']
        album = track['album']
        print(f'track: "{name}" by "{artist}" from "{album}"')

#TODO: sanitize artist name, track name, etc.
query = f"{playlists[0]['tracks'][0]['artist'].replace(' ', '+')}+{playlists[0]['tracks'][0]['name'].replace(' ', '+')}"
link = "https://www.youtube.com/results?search_query={}".format(query)

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
#TODO: add indexes to beginning of filename so that the order stays the same on the fs
ytdl_options = {'extract_audio': True, 'format': 'bestaudio', 'outtmpl': '%(title)s.mp3'}

ytdl = yt_dlp.YoutubeDL(ytdl_options)
ytdl.download(chosen)

driver.quit()
