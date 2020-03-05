import argparse
import os
import random
import schedule
import spotipy
import time
import yaml

CONFIG_FILE = 'config.yml'
SCOPE = 'playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private'
REDIRECT_URI = 'http://localhost/'


class Spoticopy:
    def __init__(self, args, config_path=CONFIG_FILE):
        self.args = args

        config = yaml.safe_load(open(config_path))
        self.user = config['username']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.source_uri = config['source_uri']
        self.target_uri = config['target_uri']

        if args.restore:
            self.restore_backup()
        else:
            self.backup()

    def get_spotipy_instance(self):
        token = spotipy.util.prompt_for_user_token(self.user, SCOPE, client_id=self.client_id,
                                                   client_secret=self.client_secret,
                                                   redirect_uri=REDIRECT_URI)
        if token:
            return spotipy.Spotify(auth=token)
        else:
            print("[warn] Couldn't get token")
            return None

    def get_all_playlist_tracks(self, sp, uri):
        page = sp.user_playlist_tracks(self.user, uri)
        tracks = page['items']

        while page['next']:
            page = sp.next(page)
            tracks.extend(page['items'])

        return tracks

    @staticmethod
    def generate_pages(track_ids):
        return [track_ids[i * 100:(i + 1) * 100] for i in range((len(track_ids) // 100) + 1)]

    def backup(self):
        sp = self.get_spotipy_instance()

        source_list = self.get_all_playlist_tracks(sp, self.source_uri)
        source_ids = [item['track']['id'] for item in source_list]

        filename = f'.backup-{self.user}'
        with open(filename, 'w') as file:
            file.writelines(f'{track_id}\n' for track_id in source_ids)

        print(f"[info] Source list backed up to {filename}")

    def restore_backup(self):
        sp = self.get_spotipy_instance()

        ids = []
        filename = f'.backup-{self.user}'
        with open(filename, 'r') as file:
            for line in file:
                ids.append(line.strip())

        pages = self.generate_pages(ids)

        sp.user_playlist_replace_tracks(self.user, self.source_uri, [])
        for page in pages:
            sp.user_playlist_add_tracks(self.user, self.source_uri, page)

        print("[info] Backup restored to source list")

    def randomize_target(self):
        sp = self.get_spotipy_instance()

        target_list = self.get_all_playlist_tracks(sp, self.target_uri)
        target_ids = [item['track']['id'] for item in target_list]

        random.shuffle(target_ids)
        pages = self.generate_pages(target_ids)

        sp.user_playlist_replace_tracks(self.user, self.target_uri, [])
        for page in pages:
            sp.user_playlist_add_tracks(self.user, self.target_uri, page)

        print("[info] Target list randomized")

    def update_target(self):
        sp = self.get_spotipy_instance()

        source_list = self.get_all_playlist_tracks(sp, self.source_uri)
        target_list = self.get_all_playlist_tracks(sp, self.target_uri)

        source_ids = [item['track']['id'] for item in source_list]
        target_ids = [item['track']['id'] for item in target_list]

        new = [i for i in source_ids + target_ids if i not in target_ids]
        removed = [i for i in source_ids + target_ids if i not in source_ids]

        if new:
            pages = self.generate_pages(new)
            for page in pages:
                sp.user_playlist_add_tracks(self.user, self.target_uri, page)
        if removed:
            pages = self.generate_pages(removed)
            for page in pages:
                sp.user_playlist_remove_all_occurrences_of_tracks(self.user, self.target_uri, page)

        print(f"[info] Target list updated: {len(new)} tracks added and {len(removed)} tracks removed")


def parse_args():
    parser = argparse.ArgumentParser(description="Copy Spotify playlist contents between playlists.")
    subparsers = parser.add_subparsers(dest='subparser')
    schedule_parser = subparsers.add_parser('schedule',  help="schedule options to run at an interval")
    schedule_parser.set_defaults(func=schedule_tasks)

    parser.add_argument('-c', '--copy', action='store_true', help="copy all tracks from source to target playlist")
    parser.add_argument('-r', '--randomize', action='store_true', help="randomize the target playlist")
    parser.add_argument('--setup', action='store_true', help="start guided setup")
    parser.add_argument('--restore', action='store_true', help="restore backup to the source playlist")

    schedule_parser.add_argument('-c', '--copy', metavar='MINUTES', nargs='?', const=5, type=int,
                                 help="copy all tracks from source to target playlist, "
                                      "optionally with interval in minutes (default: 5)")
    schedule_parser.add_argument('-r', '--randomize', metavar='DAYS', nargs='?', const=7, type=int,
                                 help="randomize the target playlist, optionally with interval in days (default: 7)")
    return parser.parse_args()


def setup():
    config = {}
    print("Setting up spotico.py...")
    config['username'] = input("> Enter your Spotify username: ")
    print("Create an app on https://developer.spotify.com/dashboard/")
    print("Then, go into the settings of your app and set the redirect url to: http://localhost/")
    config['client_id'] = input("> Now go back to your app and locate and enter your Client ID: ")
    config['client_secret'] = input("> Enter your Client Secret: ")
    config['source_uri'] = input("> Go into Spotify and copy the URI for the SOURCE playlist through the share menu: ")
    config['target_uri'] = input("> Go into Spotify and copy the URI for the TARGET playlist through the share menu: ")

    with open(CONFIG_FILE, 'w') as file:
        yaml.dump(config, file)
    print(f"Configuration has been written to {CONFIG_FILE}! Now, Spotipy might prompt you to login and authorize "
          f"this app.\n")


def run_once(args, spc):
    if args.copy:
        spc.update_target()
    if args.randomize:
        spc.randomize_target()


def schedule_tasks(args, spc):
    if args.copy is not None and args.copy > 0:
        print(f"[info] Copying scheduled to run every {args.copy} minutes")
        schedule.every(int(args.copy)).minutes.do(spc.update_target)

    if args.randomize is not None and args.randomize > 0:
        print(f"[info] Randomization scheduled to run every {args.randomize} days")
        schedule.every(int(args.randomize)).days.do(spc.randomize_target)

    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    args = parse_args()
    if args.setup or not os.path.exists(CONFIG_FILE):
        setup()

    spc = Spoticopy(args)

    if args.subparser == 'schedule':
        args.func(args, spc)
    else:
        run_once(args, spc)


if __name__ == '__main__':
    main()
