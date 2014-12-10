#!/usr/bin/env python -u
#this tool looks up spotify playlists and clones them over to google play music
#with an acceptable degree of accuracy allowing for variations in song info
#this causes it to be pretty slow, but at least you don't have to do it by hand
#read more at the README!

import spotify
from gmusicapi import Mobileclient
from os import system
import threading
from sys import stdout

def levenshtein(a,b):
#from http://hetland.org/coding/python/levenshtein.py
#used to compare strings, similar strings return lower numbers
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

#help handle spotify login
logged_in_event = threading.Event()
def logged_in_listener(session, error_type):
    logged_in_event.set()

def get_password(prompt):
    #from http://scrollingtext.org/hiding-keyboard-input-screen
    #allows entry of password from the terminal without it printing to the screen
    system("stty -echo")
    password = raw_input(prompt)
    system("stty echo")
    return password

def login_gpm():
    #takes credentials and checks user login of Google
    username = raw_input("Enter your Google Play username: ")
    password = get_password("Enter your Google Play password: ")
    #file = open('play_creds', 'r')
    #username = file.readline().rstrip('\n')
    #password = file.readline().rstrip('\n')
    #file.close()
    gpm = Mobileclient()
    if not gpm.login(username, password):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return gpm

def login_spotify(spot):
    #takes credentials and checks user login of spotify
    username = raw_input("Enter your Spotify username: ")
    password = get_password("Enter your Spotify password: ")
    #file = open('spotify_creds', 'r')
    #username = file.readline().rstrip('\n')
    #password = file.readline().rstrip('\n')
    #file.close()
    spot.login(username, password)
    spot.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)
    while spot.connection_state != spotify.ConnectionState.LOGGED_IN:
        spot.process_events()
    if (spot.user is None):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return spot

def get_playlist(spot):
    #gets a list of all spotify playlists and allows the user to choose which one they want to clone
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
        spot.logout()
        exit()
    return spotify_playlists[option-1]

def is_similar(title1, artist1, album1, title2, artist2, album2):
    #the main comparison algorithm os the program
    #makes the judgements on whether a song is a close enough match or not

    #two thresholds explained later
    threshold1 = 14
    threshold2 = 9

    #the next few statements attempt to remove extra stuff from songs
    #"The City (Extended Mix)" may not match, so we have an alternate for each field that removes
    #things in brackets, parentheses, and things after dashes
    try:
        title1alt = title1.split("(")[0].split("[")[0]
        title2alt = title2.split("(")[0].split("[")[0]
    except:
        #if the song does not have a title then just return false
        return False
    try:
        album2alt = album2.split("(")[0].split("[")[0]
        album1alt = album1.split("(")[0].split("[")[0]
    except:
        #if one of the parts of the comparison is blank then just make everything the same
        album1, album2, album1alt, album2alt = "none", "none", "none", "none"
    try:
        artist1alt = artist1.split("(")[0].split("[")[0]
        artist2alt = artist2.split("(")[0].split("[")[0]
    except:
        #same as above
        artist1, artist2, artist1alt, artist2alt = "none", "none", "none", "none"

    #the next 16 statements modify the threshold according to the name length
    #this is to allow songs with shorter details to have less variability and
    #songs with longer details to have higher variablility
    #will probably replace with ratio based on length so the threshold
    #is dynamically modified
    if (len(title1) < 8 or len(title1alt) < 8):
        threshold1 -= 1
        threshold2 -= 1
    if len(title2) < 8 or len(title2alt) < 8:
        threshold1 -= 1
        threshold2 -= 1
    if (len(title1) < 5 or len(title1alt) < 5):
        threshold1 -= 1
    if len(title2) < 5 or len(title2alt) < 5:
        threshold1 -= 1
    if len(artist1) < 12 or len(artist1alt) < 12:
        threshold1 -= 3
        threshold2 -= 1
    if len(artist2) < 12 or len(artist2alt) < 12:
        threshold1 -= 3
        threshold2 -= 1
    if len(title1) < 13 or len(title1alt) < 13:
        threshold1 -= 2
        threshold2 -= 1
    if len(title2) < 13 or len(title2alt) < 13:
        threshold1 -= 2
        threshold2 -= 1
    if len(album1) < 12 or len(album1alt) < 12:
        threshold1 -= 3
        threshold2 -= 1
    if len(album2) < 12 or len(album2alt) < 12:
        threshold1 -= 3
        threshold2 -= 1
    if len(artist1) > 25 or len(artist1alt) > 25:
        threshold1 += 2
        threshold2 += 1
    if len(artist2) > 25 or len(artist2alt) > 25:
        threshold1 += 2
        threshold2 += 1
    if len(title1) > 25 or len(title1alt) > 25:
        threshold1 += 3
        threshold2 += 1
    if len(title2) > 25 or len(title2alt) > 25:
        threshold1 += 3
        threshold2 += 1
    if len(album1) > 25 or len(album1alt) > 25:
        threshold1 += 2
        threshold2 += 1
    if len(album2) > 25 or len(album2alt) > 25:
        threshold1 += 2
        threshold2 += 1

    #this is the main comparison logic
    #first compares the two for an exact match based off of title and artist
    #next it uses the alternate titles and artists in a direct comparison
    #third it takes the sum of the levenstein calculations for the differences in the
    #title, artist, and album and compares it to the first threshold
    #finally levenstien calculations are done for the alternatives and compared against
    #the thresholds individually
    if title1 is title2 and artist1 is artist2 and not artist2 is "none":
        return True
    elif title1alt is title2alt and artist1alt is artist2alt and not artist2alt is "none":
        return True
    elif (levenshtein(title1,title2) + levenshtein(artist1, artist2) + levenshtein(album1, album2) < threshold1):
        return True
    elif (levenshtein(title1alt,title2alt) < threshold2 and levenshtein(artist1alt, artist2alt) < threshold2 and levenshtein(album1alt, album2alt) < threshold2):
        return True
    else:
        #if there is no match then the function returns false
        return False

def main():
    #setup spotify config and initialize session
    config = spotify.Config()
    config.user_agent = 'spotify2playmusic'
    config.tracefile = b'/tmp/libspotify-trace.log'
    spot = spotify.Session(config=config)

    #log in and get playlist choice for cloning
    gpm = login_gpm()
    spot = login_spotify(spot)
    playlist = get_playlist(spot)

    #get google play playlist names and compare them to the chosen list
    #if there is a playlist with the same name already in google play then say so and exit
    gpm_playlist_names = []
    for gpm_playlist in gpm.get_all_playlists():
        gpm_playlist_names.append(gpm_playlist['name'])
    if playlist.load().name in gpm_playlist_names:
        print("Playlist already exists in Google Play... exiting")
        exit()

    #there will be two lists: one of tracks to be added and another
    #of songs that could not be matched
    to_add_list = []
    unmatched_tracks = []

    #searches user uploaded music first
    print("Searching in uploaded music first...")
    gpm_local = gpm.get_all_songs()
    print("Database loaded!")
    progress = 0
    for track in playlist.load().tracks:
        progress += 1
        track = track.load()
        title = track.name
        artist = track.artists[0].load().name
        album = track.album.load().name
        #for progress
        stdout.flush()
        stdout.write("%i%% - %s - %s     \r" % (((float(progress) / float(len(playlist.load().tracks))) * 100.0), title, artist))
        unmatched = True
        top5 = {}
        to_push_id = ""
        #checks against every song in the google play library and finds the
        #top 5 hits, then the one with the lowest levenshtein number is chosen
        for i in gpm_local:
            if is_similar(title, artist, album, i['title'], i['artist'], i['album']):
                print(" - Found a match in uploaded library: " + i['title'] + " - " + i['artist'] + "     ")
                unmatched = False
                top5[i['title']] = i['id']
                to_push_id = i['id']
            if len(top5) == 5:
                break
        if len(top5) > 1:
            lowest_score = 999999
            winning_track = ""
            for top in top5.keys():
                val = levenshtein(title, top)
                if val < lowest_score:
                    lowest_score = val
                    to_push_id = top5[top]
                    winning_track = top
            if winning_track is not "":
                print("Going with the closest match: " + winning_track)
        if unmatched:
            unmatched_tracks.append(track)
        if to_push_id is not "":
            to_add_list.append(to_push_id)

    #all remaining unmatched tracks are searched in All Access
    print("Now searching All Access for the remaining tracks...")
    progress = 0
    for track in unmatched_tracks:
        progress +=1
        track = track.load()
        title = track.name
        artist = track.artists[0].load().name
        album = track.album.load().name
        #only searches for title and artist because google play does not return
        #the correct results when album is included
        query = title + " " + artist
        #for progress
        stdout.flush()
        stdout.write("%i%% - %s - %s     \r" % (((float(progress) / float(len(playlist.load().tracks))) * 100.0), title, artist))
        unmatched = True
        #does two comparisons: one with the album and one where they both have
        #the same album, this will increase the chance of matching
        #I trust google's search function :)
        try:
            result = gpm.search_all_access(query, max_results = 10)['song_hits'][0]['track']
            if is_similar(title, artist, album, result['title'], result['artist'], result['album']):
                print(" - Found a match in All Access: " + result['title'] + " - " + result['artist'] + "     ")
                unmatched = False
                unmatched_tracks.remove(track)
                to_add_list.append(result['nid'])
        except:
            pass

        if len(unmatched_tracks) != 0 and unmatched == True:
            try:
                result = gpm.search_all_access(query, max_results = 10)['song_hits'][0]['track']
                if is_similar(title, artist, "analbumthebest", result['title'], result['artist'], "analbumthebest"):
                    print(" - Found a match in All Access: " + result['title'] + " - " + result['artist'] + "     ")
                    unmatched = False
                    unmatched_tracks.remove(track)
                    to_add_list.append(result['nid'])
            except:
                pass

    #add the new playlist and all of the identified songs songs to it
    gpm_new_playlist_id = gpm.create_playlist(playlist.load().name)
    print("Adding matched songs to playlist\n")
    for to_add in to_add_list:
        gpm.add_songs_to_playlist(gpm_new_playlist_id, to_add)

    #show the unmatched tracks
    print("Unmatched tracks:")
    for unmatched_track in unmatched_tracks:
        print(unmatched_track.load().name + " - " + unmatched_track.load().artists[0].load().name)

main()
