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

def get_playlist(spot):
    playlists = spot.playlist_container
    playlists.load()
    spotify_playlists = []
    count = 0
    for playlist in playlists:
        if type(playlist) is spotify.playlist.Playlist:
            spotify_playlists.append(playlist)
            print(str(count+1) + ". " + playlist.load().name)
            count += 1
    option = -1
    while (option < 0 or option > (count+1)):
        option = input("Playlist to duplicate (enter a number, 0 to exit): ")
        if (option < 0 or option > (count+1)):
            print("Invalid option, " + option + " try again")
    if option == 0:
        print("Bye!")
        exit()
    return spotify_playlists[option-1]

def is_similar(title1, artist1, album1, title2, artist2, album2):
    title1 = title1.split("(")[0]
    artist1 = artist1.split("(")[0]
    album1 = album1.split("(")[0]
    title2 = title2.split("(")[0]
    artist2 = artist2.split("(")[0]
    album2 = album2.split("(")[0]

    if (levenshtein(title1,title2) < 4 and levenshtein(artist1, artist2) < 5 and levenshtein(album1, album2) < 5):
        return True
    else:
        return False

def main():
    config = spotify.Config()
    config.user_agent = 'spotify2playmusic'
    config.tracefile = b'/tmp/libspotify-trace.log'
    spot = spotify.Session(config=config)

    gpm = login_gpm()
    spot = login_spotify(spot)
    playlist = get_playlist(spot)

    gpm_playlist_names = []
    for gpm_playlist in gpm.get_all_playlists():
        gpm_playlist_names.append(gpm_playlist['name'])
    if playlist.load().name in gpm_playlist_names:
        print("Playlist already exists in Google Play... exiting")
        exit()

    gpm_new_playlist_id = gpm.create_playlist(playlist.load().name)
    to_add_list = []
    unmatched_tracks = []

    print("Searching in uploaded music first...")
    gpm_local = gpm.get_all_songs()
    for track in playlist.load().tracks:
        track = track.load()
        title = track.name
        artist = track.artists[0].load().name
        album = track.album.load().name
        query = title + " " + artist + " " + album
        print query
        unmatched = True
        for i in gpm_local:
            if is_similar(title, artist, album, i['title'], i['artist'], i['album']):
                print("Found a match in local library: " + i['title'])
                unmatched = False
                to_add_list.append(i['nid'])
                break
        if unmatched:
            unmatched_tracks.append(track)

#    print("Now searching All Access for the remaining tracks")
#    for track in unmatched_tracks:
#        track = track.load()
#        title = track.name
#        artist = track.artists[0].load().name
#        album = track.album.load().name
#        query = title + " " + artist
#        print query
#        unmatched = True
#        result = gpm.search_all_access(query, max_results = 1)['song_hits'][0]
#        if is_similar(title, artist, album, result['title'], result['artist'], result['album']):
#            print("Found a match in local library: " + i['title'])
#            unmatched = False
#            unmatched_tracks.delete(track)
#            to_add_list.append(i['nid'])
#            break

    print("Adding matched songs to playlist")
    for to_add in to_add_list:
        gpm.add_songs_to_playlist(gpm_new_playlist_id, to_add)
    print("Unmatched tracks")
    for unmatched_track in unmatched_tracks:
        print(unmatched_track.load().name)
main()
