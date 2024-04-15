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
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(path_in)
        .output(
            path_out,
            {"codec:a": "libmp3lame"}
        )
    )

    ffmpeg.execute()


def dl_track(driver, track, dir_path):
    #downloads the audio stream off youtube with whatever 
    #container yt was using

    #query = f"{track['artist']} {track['name']} {track['album']}"
    query = f"{track['artist']} {track['name']}"
    search_results = search_youtube(driver, query)
    link = search_results[0].get_attribute('href')

    ytdl_options = {
        'extract_audio': True,
        'format': 'bestaudio',
        'paths': {'home': dir_path}
    }
    ytdl = yt_dlp.YoutubeDL(ytdl_options)
    info = ytdl.extract_info(link, download=True)

    ytdl.close()
    return info


def dl_playlist(driver, playlist):
    pl_name = playlist['name'].replace("/", " ")
    dl_path = pathlib.Path(os.getcwd()).joinpath(pl_name)
    print(dl_path)

    track_index = 0
    for track in playlist['tracks']:
        before = time.time()
        info = dl_track(driver, track, str(dl_path.resolve()))


        source_track_path = pathlib.Path(info['requested_downloads'][0]['filepath'])

        filename_prefix = str(track_index).zfill(len(str(len(playlist['tracks']))))
        mp3_filename = filename_prefix + " - " + info['title'] + '.mp3'
        mp3_track_path = dl_path.joinpath(mp3_filename)

        convert_mp3(str(source_track_path.resolve()), str(mp3_track_path.resolve()))
        source_track_path.unlink()


        elapsed = time.time() - before
        if elapsed < min_wait:
            remainder = min_wait - elapsed
            print(f"Waiting {remainder} seconds...")
            time.sleep(remainder)

        track_index += 1


if __name__ == "__main__":
    playlists = load_playlists()
    list_playlists(playlists)

    print("Which playlist to download? Input the index: ")
    plist_index = int(input())

    driver = start_webdriver()
    playlist = playlists[plist_index]
    dl_playlist(driver, playlist)

    driver.quit()

