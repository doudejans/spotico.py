# spotico.py

spotico.py is a simple program for copying and mirroring the contents of a Spotify playlist.
This program was originally made for creating a public collaborative playlist on Spotify since playlists can't be both public and collaborative at the same time.
spotico.py solves this by mirroring a private collaborative playlist to a public playlist.
The program looks for any differences between source and target playlists and updates the target accordingly.
Furthermore, spotico.py also supports randomization of the playlist and automatic updating.

## Usage
```shell script
$ python spotico.py -h
usage: spotico.py [-h] [-c] [-i INTERVAL] [-r]

Copy Spotify playlist contents between playlists.

optional arguments:
  -h, --help            show this help message and exit
  -c, --copy            copy all tracks from source to target playlist
  -i INTERVAL, --interval INTERVAL
                        interval for which to repeat the chosen options in
                        minutes
  -r, --randomize       randomize the target playlist
```

## Requirements
spotico.py has been built and tested using Python 3.7.
The program relies on [Spotipy](https://github.com/plamere/spotipy) and [PyYAML](https://github.com/yaml/pyyaml).
```shell script
$ pip install -r requirements.txt
```

## Setup
spotico.py assumes that a `config.yml` file is present in the root folder with the following format:
```yaml
username: 'xxxxxx'
client_id: 'xxxxxx'
client_secret: 'xxxxxx'

source_uri: 'spotify:playlist:xxxxxx'
target_uri: 'spotify:playlist:xxxxxx'
```

A client ID and secret can be generated within the [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard/).
The URIs of your playlists can be copied through the share menu when right-clicking a playlist.