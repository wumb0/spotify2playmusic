#!/usr/bin/env python
import spotify
from gmusicapi import Mobileclient
from os import system
import threading

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
    #gpm = login_gpm()
    spot = login_spotify(spot)
    playlists = spot.playlist_container
    playlists.load()
    print(playlists.is_loaded)
    for playlist in playlists:
        if type(playlist) is spotify.playlist.Playlist:
            print(playlist.load().name)
main()
