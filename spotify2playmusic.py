#!/usr/bin/env python
import spotify
from gmusicapi import Mobileclient
from os import system

def get_password(prompt):
    #from http://scrollingtext.org/hiding-keyboard-input-screen
    system("stty -echo")
    password = raw_input(prompt)
    system("stty echo")
    return password

def login_gpm():
    username = raw_input("Enter your Google Play username: ")
    password = get_password("Enter your Google Play password: ")
    gpm = Mobileclient()
    if not gpm.login(username, password):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return gpm

def login_spotify():
    username = raw_input("Enter your Spotify username: ")
    password = get_password("Enter your Spotify password: ")
    spot = spotify.Session()
    if not spot.login(username, password):
        print("\nNot a valid login")
        exit()
    else:
        print("\nLogin success!")
        return spot

def main():
    gpm = login_gpm()
    spot = login_spotify()


main()
