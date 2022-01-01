# Youtube-Rewind
 
Youtube Rewind script to make a summary of the YouTube videos watched in the past year similiar to Spotify Wrapped


## Requirements
* Get an `API Key` from [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com)\
Create a key with  **YouTube Data API v3** access
 * Get your  `watch-history.JSON` from [Google Takeout](https://takeout.google.com)\
 Choose only: *YouTube and YouTube Music* -> *history*

## Usage
```bash
./main.py --year 2021 --api-key ./api-key.txt --data-file ./watch-history.json
```
