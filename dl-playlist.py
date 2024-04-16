#!/bin/python3

import time
import json
import pathlib
import urllib
import argparse
import sys
import re

import yt_dlp
from ffmpeg import FFmpeg

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from typing import Dict, List


MIN_WAIT = 10

def load_playlists(path: str):
    plist_file = open(path, 'r')
    playlists = json.loads(plist_file.read())
    plist_file.close()

    return playlists


def search_playlist(playlists: List[Dict], name: str):
    return [item for item in playlists if item['name'].startswith(name)]


def search_playlist_regex(playlists: List[Dict], regex: str):
    matcher = re.compile(regex)
    return [item for item in playlists if matcher.match(item['name']) is not None]


def list_playlists(playlists: List[Dict]):
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


def search_youtube(driver: webdriver.chromium.webdriver.ChromiumDriver, query: str):
    query = urllib.parse.quote_plus(query)
    link = "https://www.youtube.com/results?search_query={}".format(query)

    driver.get(link)
    search_results = driver.find_elements(by=By.CSS_SELECTOR, value="a[id='video-title']")

    #for now, just return the first result
    ret_link = search_results[0].get_attribute('href')
    return ret_link


def convert_mp3(path_in: str, path_out: str):
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


def dl_track(driver: webdriver.chromium.webdriver.ChromiumDriver, track, dir_path: str):
    #downloads the audio stream off youtube with whatever 
    #container yt was using

    #TODO: some tracks have multiple artists!!!!!
    #TODO: some tracks have multiple artists!!!!!
    #TODO: some tracks have multiple artists!!!!!
    query = f"{track['artist']} {track['name']}"
    link = search_youtube(driver, query)

    ytdl_options = {
        'extract_audio': True,
        'format': 'bestaudio',
        'paths': {'home': dir_path}
    }
    ytdl = yt_dlp.YoutubeDL(ytdl_options)
    info = ytdl.extract_info(link, download=True)

    ytdl.close()
    return info


def dl_playlist(driver: webdriver.chromium.webdriver.ChromiumDriver,
                playlists: List[Dict], dl_dir: str):

    for playlist in playlists:
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

    parser.add_argument("-n", "--playlist-name", dest="plist_name",
                        help="Name of the playlist to download in the JSON. Matches if playlist starts with this name.",
                        type=str,
                        required=True)

    parser.add_argument("-r", "--regex", dest="search_regex",
                        help="If passed, the name of the playlist will instead be interpreted as a regular expression.",
                        type=bool,
                        nargs='?',
                        const=True,
                        default=False)

    parser.add_argument("-c", "--command", dest="command",
                        help="Operation to perform on the playlist.",
                        type=str,
                        choices=['download', 'search'],
                        required=True)

    parser.add_argument("-t", "--min-wait-time", dest="min_wait",
                        help="In seconds. Minimum time to enforce between each track that was 'processed'.",
                        type=int,
                        default=MIN_WAIT)

    args = parser.parse_args()
    #uhhhhh... yeah.
    MIN_WAIT = args.min_wait

    playlists = load_playlists(args.playlist_path)

    matches = None
    if args.search_regex:
        matches = search_playlist_regex(playlists, args.plist_name)
    else:
        matches = search_playlist(playlists, args.plist_name)

    if args.command == "search":
        print(f"{len(matches)} matches.")

        names = [item['name'] for item in matches]
        print(f"Found: {names}.")

        print("More verbose output:")
        print(json.dumps(matches, indent=4, ensure_ascii=False))

    elif args.command == "download":
        driver = start_webdriver()
        names = [item['name'] for item in matches]

        print(f"Downloading {names}...")
        dl_playlist(driver, matches, args.dl_dir_path)

        driver.quit()

