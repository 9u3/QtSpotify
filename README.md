# QtSpotify

## A Spotify player made entirely using PyQt5 and Spotipy.

![Preview](https://user-images.githubusercontent.com/48463140/168524278-495d8866-bb86-4b0a-980b-911808c99d15.png)

## Notes
- You need premium to take full advantage of this program.

## Bugs
- Changing playlist can sometimes not update the song list. ( a restart can fix this )

## Current Features
- Playing Songs ( duh )
- Playlists ( Playing/viewing )
- Song Searching
- Song Selector

## Features to be added
- Creating playlists
- Shuffling / looping
- Change playback device

## Installation.
1. Install PyQt5 ( ` pip install PyQt5 ` )
2. Install Spotipy ( ` pip install spotipy ` )

## First time steps
1. Make a spotify developer app ( https://developer.spotify.com/dashboard/ )
2. Get a client secret and token
3. Set redirect URL to `http://127.0.0.1:8000`
4. Add them to `main.py` in the correct place
5. Run `main.py`
6. Login to spotify and give required permissions
