import pathlib

import feedparser
from moviepy.editor import *
from yt_dlp import YoutubeDL

from file_handler import read_already_watched, read_ignored, read_channel_lists, read_not_working_videos, \
    read_keywords_to_skip
from youtubedl_handler import download_videos


def download_and_sponsorblock_videos(channels, category):
    # for each channel in the list of channels, read rss feed and print the title of the first item
    # if category is not an existing folder, create it
    if pathlib.Path(category).is_dir() is False:
        pathlib.Path(category.strip(".txt")).mkdir(parents=True, exist_ok=True)
    os.chdir(category)
    for channel in channels:

        channel_rss_feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel)

        for entry in channel_rss_feed['entries']:
            download_videos(entry)

    os.chdir("../")


def main():
    read_already_watched()
    read_ignored()
    read_not_working_videos()
    read_keywords_to_skip()

    channel_file_dict = read_channel_lists()

    download_dir = f"{os.path.expanduser('~')}/Videos/Youtube"
    os.chdir(download_dir)

    # for each entry in channel_file_dict
    for channel in channel_file_dict:
        download_and_sponsorblock_videos(channel_file_dict[channel], channel.strip(".txt"))


# if something is regionlocked you can check for it in the Exception using Exception as e
# and ignore it or add to list of regionlocked
# if you want to use a vpn
def tester():
    # help(yt_dlp.YoutubeDL)
    opt = {
        "quiet": "true"
    }
    with YoutubeDL(opt) as ydl:
        try:
            ydl.extract_info("https://www.youtube.com/watch?v=aAZy4Un5ipo", download=False)

        # todo create regionlocked list and make an option to skip regionlocked videos
        # todo create different lists for different blocked videos and skip them like ignored
        # todo add option to rerun blocked videos of all kinds (excluding shorts)
        except Exception as e:

            return


if __name__ == '__main__':
    main()
    # tester()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
