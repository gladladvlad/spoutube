#!/bin/python3

import os
import time
import json
import pathlib
import urllib

import yt_dlp
from ffmpeg import FFmpeg

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


min_wait = 7.5

def load_playlists():
    plist_file = open('spotify-playlists.json', 'r')
    playlists = json.loads(plist_file.read())
    plist_file.close()

    return playlists


def list_playlists(playlists):
    index = 0
    for plist in playlists:
        #print('---')
        print(str(index) + " " + plist['name'])
        #print('---')

       #for track in plist['tracks']:
       #    artist = track['artist']
       #    name = track['name']
       #    album = track['album']
       #    print(f'track: "{name}" by "{artist}" from "{album}"')

        index += 1


def start_webdriver():
    webdriver_options = Options()
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-crash-reporter")

    driver = webdriver.Chrome(options=webdriver_options)
    driver.implicitly_wait(0.5)

    return driver


def search_youtube(driver, query):
    query = urllib.parse.quote_plus(query)
    link = "https://www.youtube.com/results?search_query={}".format(query)

    driver.get(link)
    search_results = driver.find_elements(by=By.CSS_SELECTOR, value="a[id='video-title']")

    return search_results


def convert_mp3(path_in, path_out):
    path_in = pathlib.Path(path_in)
    path_out = pathlib.Path(path_out)

    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(str(path_in.resolve()))
        .output(
            str(path_out.resolve()),
            {"codec:a": "libmp3lame"}
        )
    )

    ffmpeg.execute()


def dl_track(driver, track, ytdl_options):
    #downloads the audio stream off youtube with whatever 
    #container yt was using

    #query = f"{track['artist']} {track['name']} {track['album']}"
    query = f"{track['artist']} {track['name']}"
    search_results = search_youtube(driver, query)
    link = search_results[0].get_attribute('href')

    ytdl = yt_dlp.YoutubeDL(ytdl_options)
    ytdl.download(link)


def dl_playlist(driver, playlist):
    pl_name = playlist['name'].replace("/", " ")
    dl_path = pathlib.Path(os.getcwd()).joinpath(pl_name)
    print(dl_path)

    track_index = 0
    for track in playlist['tracks']:
        filename_prefix = str(track_index).zfill(len(str(len(playlist['tracks']))))

        before = time.time()
        ytdl_options = {
            'extract_audio': True,
            'format': 'bestaudio',
            'outtmpl': f'{filename_prefix} - %(title)s.mp3',
            'paths': {'home': str(dl_path.resolve())}
        }
        dl_track(driver, track, ytdl_options)
        after = time.time()
        elapsed = after - before

        if elapsed < min_wait:
            time.sleep(min_wait - elapsed)

        track_index += 1


playlists = load_playlists()
list_playlists(playlists)

print("Which playlist to download? Input the index: ")
plist_index = int(input())

driver = start_webdriver()
playlist = playlists[plist_index]
dl_playlist(driver, playlist)

driver.quit()

#fin = "/home/vlad/workspace/spoutube/test.opus"
#fout = "/home/vlad/workspace/spoutube/out.mp3"
#
#convert_mp3(fin, fout)

