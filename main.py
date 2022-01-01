#!/usr/bin/env python3

import json
import math
import pickle
from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from itertools import zip_longest
import isodate
from tqdm import tqdm
from argparse import ArgumentParser
import googleapiclient.discovery


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


@dataclass
class YoutubeRewind:
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    VIDEOS_PER_QUERY = 50
    year: str
    watch_history: list[dict]
    api_key: str

    def __post_init__(self):
        self.youtube = googleapiclient.discovery.build(
            self.API_SERVICE_NAME, self.API_VERSION, developerKey=self.api_key)

    def run(self) -> None:
        results = defaultdict(int)
        existing_videos = [(video['subtitles'][0]['name'], self.get_video_id(video['titleUrl']))
                           for video in self.watch_history
                           if video['time'].startswith(self.year) and 'subtitles' in video and 'titleUrl' in video]
        
        iterations = math.ceil(len(existing_videos)/self.VIDEOS_PER_QUERY)
        for group in tqdm(grouper(existing_videos, self.VIDEOS_PER_QUERY), total=iterations):
            video_ids = [video[1] for video in group if video]
            videos_length = (self.get_videos_length(video_ids))
            for (youtuber, _), video_length in zip(group, videos_length):
                results[youtuber] += video_length

        pickle.dump(results, open('results.pkl', 'wb'))
        self.print_stats(results)

    def get_videos_length(self, video_ids: list[str]) -> int:
        request = self.youtube.videos().list(
            part="contentDetails",
            id=','.join(video_ids)
        )
        data = request.execute()
        durations = []
        for row in data['items']:
            duration = row['contentDetails']['duration']
            duration = isodate.parse_duration(duration)
            video_dur = duration.total_seconds()
            durations.append(video_dur)
        return durations

    @staticmethod
    def get_video_id(url: str) -> str:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        return qs['v'][0]

    @staticmethod
    def print_stats(results: dict[str, int]) -> None:
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True))
        for k, v in sorted_results.items():
            print(f'{k}: {round(v/60)}')

        total_watch_time = round(sum(results.values()) / 60)
        print(f'Total watch time: {total_watch_time} minutes')


def main():
    parser = ArgumentParser()
    parser.add_argument('-k', '--api-key', type=str, default='./api-key.txt',
                        help='file with YouTube Data API v3 API KEY Get it here: https://console.cloud.google.com/apis/library/youtube.googleapis.com')
    parser.add_argument('-d', '--data-file', type=str, default='./watch-history.json',
                        help='YouTube watch history JSON file Get it here: https://takeout.google.com')
    parser.add_argument('-y', '--year', type=str,
                        default='2021', help='Year to get rewind stats')
    args = parser.parse_args()

    with open(args.api_key) as f:
        api_key = f.read()
    watch_history = json.load(open(args.data_file))
    rewind = YoutubeRewind(args.year, watch_history, api_key)
    rewind.run()


if __name__ == '__main__':
    main()
