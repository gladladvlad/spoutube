# spoutube
### Download your Spotify playlists off YouTube.

This script uses a headless Google Chrome instance to search for the songs on YouTube. So if you have any security or privacy concerns regarding that, maybe don't use this lol.

This README.md is a work in progress. I also didn't test this on other systems so maybe I missed some obscure dependencies in the `Setup` section.

### Setup:
Create a python venv:  
    `python -m venv spoutube-venv`

Activate it:  
    `spoutube-venv/Scripts/activate.bat` on Windows  
    OR  
    `source ./spoutube-venv/bin/activate` on Linux  

In the same terminal instance, install all libs:  
    `python -m pip install -r requirements.txt`  

It's important to make sure you run this command immediately after you run 'activate' if you don't want these libraries installed system-wide.

And I guess you need Google Chrome installed for Selenium.

### Usage/examples:
First off, you'll need to export your playlists with the wonderful tool here:  
https://dev.peterfiorella.com/spotifyexport/public/

The website above is not hosted by me and I have no affiliation with this person. I just use the tool.

To download all playlists (read from `"./my-songs.json"`) that contain the word 'banger' somewhere in the name into path `"./path/to/dir"`:  
`python3 ./dl-playlist.py -i './my-songs.json' -o './path/to/dir' -n '.?bangers.?' --regex --command download`

Arguments explained:

`-i`: path to the playlists JSON. If omitted, will use default value `"./spotify-playlists.json"`.  
`-o`: path to the "output" directory.  
`-n`: name of the playlist you want the script to "affect.  
`--regex`: interpret the name (from `-n` arg) as a regular expression.  
`--command`: self-explanatory: download the playlist. This arg only supports `download` and `search` but might be updated in the future. Maybe.  
