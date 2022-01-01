#!/usr/bin/env python3

import json
from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import isodate
from tqdm import tqdm
from argparse import ArgumentParser
import googleapiclient.discovery


@dataclass
class YoutubeRewind:
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    year: str
    watch_history: list[dict]
    api_key: str

    def __post_init__(self):
        self.youtube = googleapiclient.discovery.build(
            self.API_SERVICE_NAME, self.API_VERSION, developerKey=self.api_key)

    def run(self) -> None:
        results = defaultdict(int)
        for video in tqdm(self.watch_history):
            if video['time'].startswith(self.year) and 'subtitles' in video:
                youtuber = video['subtitles'][0]['name']
                results[youtuber] += self.get_video_length(video['titleUrl'])

        self.print_stats(results)

    def get_video_length(self, url: str) -> int:
        request = self.youtube.videos().list(
            part="contentDetails",
            id=self.get_video_id(url)
        )
        data = request.execute()
        try:
            duration = data['items'][0]['contentDetails']['duration']
            duration = isodate.parse_duration(duration)
            video_dur = duration.total_seconds()
            return video_dur
        except:
            return 0

    @staticmethod
    def get_video_id(url: str) -> str:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        return qs['v']

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
    rewind = YoutubeRewind(args.year, watch_history[:1], api_key)
    rewind.run()


if __name__ == '__main__':
    main()
