#!/bin/python3

import os
import time
import json
import pathlib
import urllib
import argparse
import sys

import yt_dlp
from ffmpeg import FFmpeg

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


MIN_WAIT = 7.5

def load_playlists(path):
    plist_file = open(path, 'r')
    playlists = json.loads(plist_file.read())
    plist_file.close()

    return playlists


def list_playlists(playlists):
    index = 0
    for plist in playlists:
        #print('---')
        print(str(index) + "\t" + plist['name'])
        #print('---')

        #for track in plist['tracks']:
        #   artist = track['artist']
        #   name = track['name']
        #   album = track['album']
        #   print(f'track: "{name}" by "{artist}" from "{album}"')

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


def dl_playlist(driver, playlist, dl_dir):
    pl_name = playlist['name'].replace("/", " ")
    dl_path = pathlib.Path(dl_dir).joinpath(pl_name)

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
        if elapsed < MIN_WAIT:
            remainder = MIN_WAIT - elapsed
            print(f"Waiting {remainder} seconds...")
            time.sleep(remainder)

        track_index += 1


if __name__ == "__main__":
    description = "Reads a spotify-playlists.json in the same folder \
    and, for each entry, look up the same song on YouTube and download \
    the audio stream then convert it to mp3."

    parser = argparse.ArgumentParser(
        sys.argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description)

    parser.add_argument("-o", "--out-dir", dest="dl_dir_path",
                        help="Path to dir where the playlist will be downloaded.",
                        type=str,
                        default='./')

    parser.add_argument("-i", "--input-playlist", dest="playlist_path",
                        help="Path to the JSON from where the playlists will be read.",
                        type=str,
                        default='./spotify-playlists.json')

    parser.add_argument("-p", "--playlist-index", dest="plist_index",
                        help="Index of the playlist to download in the JSON. Omit this to list the playlists.",
                        type=int,
                        default=None)

    parser.add_argument("-c", "--command", dest="command",
                        help="Operation to perform on the playlist.",
                        type=str,
                        choices=['list', 'download'],
                        required=True)

    parser.add_argument("-t", "--min-wait-time", dest="min_wait",
                        help="In seconds. Minimum time to enforce between each track that was 'processed'.",
                        type=int,
                        default=10)

    args = parser.parse_args()
    MIN_WAIT = args.min_wait

    playlists = load_playlists(args.playlist_path)

    if args.command == "list":
        list_playlists(playlists)

    elif args.command == "download":
        driver = start_webdriver()
        playlist = playlists[args.plist_index]
        dl_playlist(driver, playlist, args.dl_dir_path)

        driver.quit()

