from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
import datetime
import time
import os
import threading

scope = "user-read-currently-playing,user-read-playback-state,user-modify-playback-state,playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="06b55ab3a6d54fb0bb9fbafd25499978",
                                               client_secret="7ac2e2df3efb45e28e0515fbe0d238ac",
                                               redirect_uri="http://127.0.0.1:8000", scope=scope))

playlistIndex = {}

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainWindow.ui', self)
        
        self.setFixedSize(905, 466)

        username = sp.current_user()['display_name']
        
        self.setWindowTitle(f"QtSpotify / {username}")
        self.setWindowIcon(QtGui.QIcon('Spotify_Icon_RGB_Black.png'))
        self.title = self.findChild(QtWidgets.QLabel, 'songname')
        self.artist = self.findChild(QtWidgets.QLabel, 'artist')
        self.curtime = self.findChild(QtWidgets.QLabel, 'ctime')
        self.preview = self.findChild(QtWidgets.QLabel, 'preview')
        self.vol = self.findChild(QtWidgets.QLabel, 'vol')
        self.volslider = self.findChild(QtWidgets.QSlider, 'volslider')
        self.next = self.findChild(QtWidgets.QPushButton, 'next')
        self.previous = self.findChild(QtWidgets.QPushButton, 'previous')
        self.play = self.findChild(QtWidgets.QPushButton, 'play')
        self.playlist = self.findChild(QtWidgets.QLabel, 'playlist')
        self.listx = self.findChild(QtWidgets.QListWidget, 'items')
        self.search = self.findChild(QtWidgets.QLineEdit, 'search')
        self.add = self.findChild(QtWidgets.QPushButton, 'addsong')
        self.playlists = self.findChild(QtWidgets.QListWidget, 'playlists')


        self.playlists.currentTextChanged.connect(self.getPlaylistID)
        self.add.clicked.connect(self.addTrack)
        self.play.clicked.connect(self.playback)
        self.next.clicked.connect(self.nextTrack)
        self.previous.clicked.connect(self.lastTrack)
        self.listx.currentTextChanged.connect(self.getTrackID)
        self.volslider.valueChanged.connect(self.setVolume)

    def setInfo(self, title, artist, ct):
        self.title.setText(title)
        self.artist.setText(artist)
        self.curtime.setText(ct)

    def getTrackID(self, item):
        resp = sp.search(item)
        trackURI = resp['tracks']['items'][0]['uri']
        tid = trackURI.replace("spotify:track:", "")
        self.playsong(trackURI)
        print(tid, item)
        
    def getPlaylistID(self, item):
        find = playlistIndex[item]
        print(find)
        self.startplaylist("spotify:playlist:" + find)

    def setTime(self, ctime):
        self.curtime.setText("-")
        self.show()

    def setV(self, cv):
        self.vol.setText(str(cv))
        self.volslider.setValue(cv)

    def setPlaylist(self, pl):
        self.playlist.setText(pl)
        self.show()

    def setList(self, l: list):
        self.listx.clear()
        self.listx.addItems(l)

    def x(self, l):
        self.playlists.addItem(l)

    def setVolume(self, cvol):
        self.vol.setText(str(cvol))
        sp.volume(cvol)
        self.show()
   
    def startplaylist(self, track):
        cur = sp.devices()['devices'][0]['id']
        sp.start_playback(device_id=cur, context_uri=track)
        sp.shuffle(True, cur)
        lisxt = []
        def getplaylist():
            try:
                current = sp.current_user_playing_track()
                ctx = current["context"]["uri"]
                playlistid = ctx.replace("spotify:playlist:","")
                playlist = sp.playlist(playlistid)
                tracks = sp.playlist_tracks(playlistid)
                return {"name": playlist['name'], "tracks": tracks['items']}
            except TypeError as TE:
                return {"name": "---", "tracks": []}

        for track in getplaylist()["tracks"]:
            artist = track['track']['album']['artists'][0]['name']
            title = track['track']['name']
            lisxt.append(f"{artist} - {title}")
        self.setList(lisxt)

    def playsong(self, track):
        cur = sp.devices()['devices'][0]['id']
        sp.start_playback(device_id=cur, uris=[track])
        sp.shuffle(True, cur)

    def playback(self):
        isplaying = sp.current_user_playing_track()['is_playing']
        if isplaying:
            sp.pause_playback()
        else:
            sp.start_playback()

    def nextTrack(self):
        sp.next_track()

    def addTrack(self):
        query = self.search.text()
        resp = sp.search(query)
        song = resp['tracks']['items'][0]
        trackid = song['uri']
        artist = f"{song['artists'][0]['name']} - {song['name']}"
        self.listx.addItem(artist)
        sp.add_to_queue(trackid, sp.devices()['devices'][0]['id'])
        self.search.clear()

    def lastTrack(self):
        sp.previous_track()

    def setImg(self, imgURL):
        image = QImage()
        image.loadFromData(requests.get(imgURL).content)

        image_label = self.preview
        image_label.setPixmap(QPixmap(image))
        image_label.show()


    def fshow(self):
        self.show()

        

def getplaying():
    current = sp.current_user_playing_track()
    time = int(int(current["progress_ms"])/1000)
    duration = int(int(current['item']["duration_ms"])/1000)
    realduration = str(datetime.timedelta(seconds=duration))
    realtime = str(datetime.timedelta(seconds=time))
    playing = current["item"]
    artist = playing["album"]["artists"][0]["name"]
    song = playing["name"]
    songid = playing["id"]
    link = playing["external_urls"]["spotify"]
    img_lq = playing["album"]["images"][2]["url"]
    img_mq = playing["album"]["images"][1]["url"]
    img_hq = playing["album"]["images"][0]["url"]
    return {"time": realtime, "duration": realduration, "artist": artist, "name": song, "link": link, "img": {"high": img_hq, "med": img_mq, "low": img_lq}}

def getplaylist():
    try:
        current = sp.current_user_playing_track()
        ctx = current["context"]["uri"]
        playlistid = ctx.replace("spotify:playlist:","")
        playlist = sp.playlist(playlistid)
        tracks = sp.playlist_tracks(playlistid)
        return {"name": playlist['name'], "tracks": tracks['items']}
    except TypeError as TE:
        return {"name": "---", "tracks": []}

llist = []

def updatePlaylist():
    playlists = sp.current_user_playlists()
    user_id = sp.me()['id']

    for playlist in playlists['items']:
        if playlist['owner']['id'] == user_id:
            playlistname = playlist['name']
            playlistlength = playlist['tracks']['total']
            playlistid = playlist['id']
            playlistIndex[playlistname] = playlistid
            win.playlists.addItem(playlistname)

    for track in getplaylist()["tracks"]:
        artist = track['track']['album']['artists'][0]['name']
        title = track['track']['name']
        llist.append(f"{artist} - {title}")
    win.setList(llist)

def fset(t:int):
    win.setV(20)
    updatePlaylist()
    while True:
        x = getplaying()
        win.setPlaylist(getplaylist()['name'])
        win.setInfo(x['name'], x['artist'], f"{x['time']}/{x['duration']}")
        win.setImg(x['img']['med'])
        time.sleep(1)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
win.setTime(0)

thread = threading.Thread(target=fset, args=(1,))
thread.start()

sys.exit(app.exec_())









