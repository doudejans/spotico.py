# spotico.py

spotico.py is a simple program for copying and mirroring the contents of a Spotify playlist.
This program was originally made for creating a public collaborative playlist on Spotify since playlists can't be both public and collaborative at the same time.
spotico.py solves this by mirroring a private collaborative playlist to a public playlist.
The program looks for any differences between source and target playlists and updates the target accordingly.
Furthermore, spotico.py also supports randomization of the playlist and automatic updating.

## Usage
```
$ python3 spotico.py -h
usage: spotico.py [-h] [-c] [-i INTERVAL] [-r] [--setup]

Copy Spotify playlist contents between playlists.

optional arguments:
  -h, --help            show this help message and exit
  -c, --copy            copy all tracks from source to target playlist
  -i INTERVAL, --interval INTERVAL
                        interval for which to repeat the chosen options in
                        minutes
  -r, --randomize       randomize the target playlist
  --setup               start guided setup
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

The username field should simply contain your Spotify username.
A client ID and secret can be generated within the [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard/).
In the settings of your application, set the redirect url to `http://localhost/`.
When running spotico.py, you will need to authorize the app with your Spotify account.
Spotipy will then prompt for the callback url that Spotify gives after authorizing the app, which you can just copy and paste from your browser into the console.

The URIs of your playlists can be copied through the share menu when right-clicking a playlist.

### Docker
This repository contains a Dockerfile, which can be used to run your instance of spotico.py in a container.
First, make sure that spotico.py is setup and working.
Then, simply build an image:
```shell script
docker build -t spotico.py .
```
Now that you have an image tagged `spotico.py`, spin it up wherever you want:
```shell script
docker run -itd --rm --name spotico.py spotico.py
```
This command will run a container in detached mode, meaning that the container and in turn spotico.py will keep running.
By default, as can be seen in the Dockerfile, spotico.py runs every hour and does not randomize.
Please note that your configuration is copied over as well when building an image, so you should refrain from publishing the image.
