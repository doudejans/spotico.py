import argparse
import random
import spotipy
import time
import yaml

SCOPE = 'playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private'
REDIRECT_URI = 'http://localhost/'


class Spoticopy:
    def __init__(self, args, config_path='config.yml'):
        self.args = args

        config = yaml.safe_load(open(config_path))
        self.user = config['username']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.source_uri = config['source_uri']
        self.target_uri = config['target_uri']

    def run(self):
        token = spotipy.util.prompt_for_user_token(self.user, SCOPE, client_id=self.client_id,
                                                   client_secret=self.client_secret,
                                                   redirect_uri=REDIRECT_URI)
        if token:
            sp = spotipy.Spotify(auth=token)
            self.backup(sp)
            if self.args.copy:
                self.update_target(sp)
            if self.args.randomize:
                self.randomize_target(sp)
        else:
            print("Couldn't get token")

    def backup(self, sp):
        source_list = sp.playlist_tracks(self.source_uri)
        source_ids = [item['track']['id'] for item in source_list['items']]
        with open(f'.backup-{self.user}', 'w') as file:
            file.writelines(f'{track_id}\n' for track_id in source_ids)

        print("Source list backed up")

    def randomize_target(self, sp):
        target_list = sp.playlist_tracks(self.target_uri)
        target_ids = [item['track']['id'] for item in target_list['items']]

        random.shuffle(target_ids)
        sp.user_playlist_replace_tracks(self.user, self.target_uri, target_ids)

        print("Target list randomized")

    def update_target(self, sp):
        source_list = sp.playlist_tracks(self.source_uri)
        target_list = sp.playlist_tracks(self.target_uri)

        source_ids = [item['track']['id'] for item in source_list['items']]
        target_ids = [item['track']['id'] for item in target_list['items']]

        new = [i for i in source_ids + target_ids if i not in target_ids]
        removed = [i for i in source_ids + target_ids if i not in source_ids]

        if new:
            sp.user_playlist_add_tracks(self.user, self.target_uri, new)
        if removed:
            sp.user_playlist_remove_all_occurrences_of_tracks(self.user, self.target_uri, removed)

        print(f"Target list updated: {len(new)} tracks added and {len(removed)} tracks removed")


def parse_args():
    parser = argparse.ArgumentParser(description="Copy Spotify playlist contents between playlists.")
    parser.add_argument('-c', '--copy', action='store_true', help="copy all tracks from source to target playlist")
    parser.add_argument('-i', '--interval', type=int,
                        help="interval for which to repeat the chosen options in minutes")
    parser.add_argument('-r', '--randomize', action='store_true', help="randomize the target playlist")
    return parser.parse_args()


def main():
    spc = Spoticopy(parse_args())

    if spc.args.interval:
        while True:
            start_time = time.time()
            refresh_interval = spc.args.interval * 60.0
            spc.run()
            time.sleep(refresh_interval - ((time.time() - start_time) % 60.0))
    else:
        spc.run()


if __name__ == '__main__':
    main()
