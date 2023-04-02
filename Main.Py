import pathlib

import feedparser
from moviepy.editor import *
from yt_dlp import YoutubeDL

from file_handler import read_config_files, read_channel_dict, read_legacy_channel_converter_dict_lists, \
    create_channels_from_new_format, read_legacy_channel_lists, save_channel_dict, save_legacy_converter_dict
from youtubedl_handler import download_videos


def download_and_sponsorblock_videos(categories):
    # for each channel in the list of channels, read rss feed and print the title of the first item
    # if category is not an existing folder, create it
    for category in categories:

        if pathlib.Path(category).is_dir() is False:
            pathlib.Path(category).mkdir(parents=True, exist_ok=True)
        os.chdir(category)
        for channel in categories[category]:
            for key in channel:

                channel_rss_feed = get_channel_feed(channel[key])

                for entry in channel_rss_feed['entries']:
                    download_videos(entry)

        os.chdir("../")


def get_channel_feed(channel):
    channel_rss_feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel)
    return channel_rss_feed


def main():
    read_config_files()

    # legacy
    print("checking for channels using the legacy channel format")
    channel_dict = create_channel_dict_from_legacy()

    print("got legacy channels")
    # new
    print("checking for newly added channels using the new format")
    channel_dict = create_channels_from_new_format(channel_dict)
    print("all channels added")

    download_dir = f"{os.path.expanduser('~')}/Videos/Youtube"
    os.chdir(download_dir)

    download_and_sponsorblock_videos(channel_dict)




# for each entry in channel_file_dict
#     for channel in channel_dict:
#       download_and_sponsorblock_videos(legacy_channel_dict[channel], channel.strip(".txt"))


def create_channel_dict_from_legacy():
    channel_dict: dict[str, list[dict[str, str]]] = read_channel_dict()
    legacy_channel_dict = read_legacy_channel_lists()
    if len(legacy_channel_dict) == 0:
        return channel_dict
    legacy_converter_dict: dict[str, dict[str, str]] = read_legacy_channel_converter_dict_lists()

    for category in legacy_channel_dict:

        if category not in channel_dict:
            channel_dict[category] = []
        if category not in legacy_converter_dict:
            legacy_converter_dict[category] = {}

        for channel in legacy_channel_dict[category]:

            if channel.rstrip("\n") not in legacy_converter_dict[category]:
                feed: dict = get_channel_feed(channel)['feed']
                channel_name: str = feed['title']
                channel_dict[category].append({channel_name: channel.rstrip("\n")})
                legacy_converter_dict[category][channel.rstrip("\n")] = channel_name
                # channel_dict[category].append()
    save_channel_dict(channel_dict)
    save_legacy_converter_dict(legacy_converter_dict)
    return channel_dict


# test area, gets reused whenever a bug exists
def _tester():
    # help(yt_dlp.YoutubeDL)
    opt = {
        "quiet": "true"
    }
    with YoutubeDL(opt) as ydl:
        try:
            info = ydl.extract_info("https://youtu.be/6yUj2diY9y8", download=False)
            print(info['channel_id'])
        except Exception as e:

            return


if __name__ == '__main__':
    main()
    # _tester()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
