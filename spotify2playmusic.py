#!/usr/bin/env python
import spotify
from gmusicapi import Mobileclient
from os import system
import threading

def levenshtein(a,b):
#from http://hetland.org/coding/python/levenshtein.py
    n, m = len(a), len(b)
    if n > m:
        a,b = b,a
        n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]

logged_in_event = threading.Event()
def logged_in_listener(session, error_type):
    logged_in_event.set()

def get_password(prompt):
    #from http://scrollingtext.org/hiding-keyboard-input-screen
    system("stty -echo")
    password = raw_input(prompt)
    system("stty echo")
    return password

def login_gpm():
    #username = raw_input("Enter your Google Play username: ")
    #password = get_password("Enter your Google Play password: ")
    file = open('play_creds', 'r')
    username = file.readline().rstrip('\n')
    password = file.readline().rstrip('\n')
    file.close()
    gpm = Mobileclient()
    if not gpm.login(username, password):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return gpm

def login_spotify(spot):
    #username = raw_input("Enter your Spotify username: ")
    #password = get_password("Enter your Spotify password: ")
    file = open('spotify_creds', 'r')
    username = file.readline().rstrip('\n')
    password = file.readline().rstrip('\n')
    file.close()
    spot.login(username, password)
    spot.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)
    while not logged_in_event.wait(0.1):
        spot.process_events()
    if (spot.user is None):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return spot

def main():
    config = spotify.Config()
    config.user_agent = 'spotify2playmusic'
    config.tracefile = b'/tmp/libspotify-trace.log'
    spot = spotify.Session(config=config)
    gpm = login_gpm()
    spot = login_spotify(spot)
    playlists = spot.playlist_container
    playlists.load()
    spotify_playlists = []
    count = 0
    for playlist in playlists:
        if type(playlist) is spotify.playlist.Playlist and playlist.load().name == "Test Playlist": #for testing
            count += 1
            spotify_playlists.append(playlist)
            print(count + "." + playlist.load().name)

#            for track in playlist.load().tracks:
#                printstr = ""
#                printstr += track.load().name + " - "
#                printstr += track.load().artists[0].load().name + " - "
#                printstr += track.load().album.load().name
#                print(printstr)
main()
