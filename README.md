# spotico.py

spotico.py is a simple program for copying and mirroring the contents of a Spotify playlist.
This program was originally made for creating a public collaborative playlist on Spotify since playlists can't be both public and collaborative at the same time.
spotico.py solves this by mirroring a private collaborative playlist to a public playlist.
The program looks for any differences between source and target playlists and updates the target accordingly.
Furthermore, spotico.py also supports randomization of the playlist and scheduling these operations.

## Usage

```shell script
python spotico.py [-c] [-r]
```

The `-c` option will copy any new songs from the source to the target playlist.
The `-r` option will randomize the order of the target playlist.
It is also possible to continuously run these options at an interval:

```shell script
python spotico.py schedule [-c [MINUTES]] [-r [DAYS]]
```

To view all options, use the `-h` option.

## Requirements

spotico.py has been written and tested using Python 3.7.
The program relies on [Spotipy](https://github.com/plamere/spotipy) and [PyYAML](https://github.com/yaml/pyyaml).

```shell script
pip install -r requirements.txt
```

## Setup

If you run spotico.py for the first time, the script will guide you step by step to generate a configuration file.
spotico.py assumes that a `config.yml` file is present in the current directory with the following format:

```yaml
client_id: 'xxxxxx'
client_secret: 'xxxxxx'

source_uri: 'spotify:playlist:xxxxxx'
target_uri: 'spotify:playlist:xxxxxx'
```

A client ID and secret can be generated within the [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard/).
In the settings of your application, set the redirect url to `http://localhost:8080/`.
When running spotico.py, you will need to authorize the app with your Spotify account.
Spotipy will then prompt for the callback url that Spotify gives after authorizing the app, which you can just copy and paste from your browser into the console.

The URIs of your playlists can be copied through the share menu when right-clicking a playlist.

### Docker

This repository contains a Dockerfile, which can be used to run your instance of spotico.py in a container.
First, make sure that spotico.py is set up and working.
Then, simply build an image:

```shell script
docker build -t spotico.py .
```

Now that you have an image tagged `spotico.py`, spin it up wherever you want:

```shell script
docker run -itd --restart unless-stopped --name spotico.py spotico.py
```

This command will run a container in detached mode, meaning that the container and in turn spotico.py will keep running.
By default, as can be seen in the Dockerfile, spotico.py runs on the default schedule (copying every 5 minutes and randomizing every 7 days).
Please note that your configuration is copied over as well when building an image, so you should refrain from publishing the image.

## Backups

When starting, spotico.py will automatically back up all tracks in your source list to a file in your current directory called `.backup`.
In case you need to restore this backup, simply run:

```shell script
python spotico.py --restore
```

Adding the `-c` flag will also immediately restore the contents to the target list.
