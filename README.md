spotify2playmusic.py
====================
I couldn't find a tool anywhere to do this... so I took a day and wrote one.<br>
This will allow you to log into your Spotify and Google Play Music accounts and select a playlist from Spotify to be cloned over to Google Play Music<br>
There are a few requirements...<br>

Requirements
------------
Spotify Premium<br>
A Spotify Developer Key<br>
libspotify<br>
pyspotify<br>
gmusicapi<br>
**Strongly** Recommended: Google Music All Access (has not been tested without it)

<h5>Spotify Developer Key</h5>
Go to [The Spotify Developer Page](https://devaccount.spotify.com/my-account/keys/), login, and get a key<br>
Put it in the same directory as spotify2playmusic. It won't work at all without the key.

<h5>libspotify and pyspotify</h5>
Go to the [pyspotify installation page](http://pyspotify.mopidy.com/en/latest/installation/) and follow the instructions to install libspotify and pyspotify for your OS (you will be using pip)

<h5>gmusicapi</h5>
<p>Use pip.</p>
```sh
pip install gmusicapi
```

Bugs/Limitations
----------------
- It's pretty slow, but at least you don't have to copy everything over by hand
    - It is slow because it does its best to match things. It uses the levenshtein calculation to figure out how different two strings are. That number is then used to determine if the strings are similar enough to be a match. If they are then the song is added to the array of songs to be added to the new playlist on google play music.
- Some songs don't match right. By trying to make it match variations it does its best to weed out the bad matches, sometimes it works, sometimes it doesn't. Overall it is pretty accurate though
- Sometimes it crashes randomly. No idea why.

Todos/Future Additions
----------------------
- Add the functionality to go from google play music to spotify playlists (I guess I'll have to change the name)
- Use the best match from the store and the uploaded library (compare them)
- Speed things up somehow
- Improve the matching calculation's accuracy
- Catch more unhandled errors and deal with them
- Clean up the code

Enjoy?
