import argparse
import pathlib

import feedparser
from moviepy.editor import *
from yt_dlp import YoutubeDL

import youtubedl_handler
from file_handler import read_config_files, read_channel_dict, read_legacy_channel_converter_dict_lists, \
    create_channels_from_new_format, read_legacy_channel_lists, save_channel_dict, save_legacy_converter_dict, \
    set_directories, get_download_dir
from youtubedl_handler import download_videos


def download_and_sponsorblock_videos(categories):
    # for each channel in the list of channels, read rss feed and print the title of the first item
    # if category is not an existing folder, create it
    for category in categories:

        if pathlib.Path(category).is_dir() is False:
            pathlib.Path(category).mkdir(parents=True, exist_ok=True)
        os.chdir(category)
        for channel in categories[category]:
            channel_rss_feed = get_channel_feed(categories[category][channel])

            for entry in channel_rss_feed['entries']:
                download_videos(entry, category)

        os.chdir("../")


def get_channel_feed(channel):
    channel_rss_feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel)
    return channel_rss_feed


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_dir", help="the location of the config, default is in the program src directory")
    parser.add_argument("--download_dir", help="directory to download to, default is ~/Videos/Youtube")
    parser.add_argument("--simulate",
                        help="simulates the values to check that you didn't mistakenly add a broken or incorrect path")
    args = parser.parse_args()
    download_dir = args.download_dir
    config_dir = args.config_dir
    simulate = args.simulate
    result = set_directories(download_dir, config_dir, simulate)
    return result



def main():
    if not init():
        return
    read_config_files()

    # legacy
    print("checking for channels using the legacy channel format")
    channel_dict = create_channel_dict_from_legacy()

    print("got legacy channels")
    # new
    print("checking for newly added channels using the new format")
    channel_dict = create_channels_from_new_format(channel_dict)
    print("all channels added")

    download_dir = get_download_dir()
    os.chdir(download_dir)

    download_and_sponsorblock_videos(channel_dict)


def create_channel_dict_from_legacy():
    channel_dict: dict[str, dict[str, str]] = read_channel_dict()
    legacy_channel_dict = read_legacy_channel_lists()
    if len(legacy_channel_dict) == 0:
        return channel_dict
    legacy_converter_dict: dict[str, dict[str, str]] = read_legacy_channel_converter_dict_lists()

    for category in legacy_channel_dict:

        if category not in channel_dict:
            channel_dict[category] = {}
        if category not in legacy_converter_dict:
            legacy_converter_dict[category] = {}

        for channel in legacy_channel_dict[category]:

            if channel.rstrip("\n") not in legacy_converter_dict[category]:
                feed: dict = get_channel_feed(channel)['feed']
                channel_name: str = feed['title']
                if channel_name not in channel_dict[category]:
                    channel_dict[category][channel_name] = channel.rstrip("\n")
                elif channel_name in channel_dict[category]:
                    if channel_dict[category][channel_name] != channel:
                        counter = 0
                        while channel_name + "_" + str(counter) in channel_dict[category]:
                            if channel_dict[category][channel_name + "_" + str(counter)] != channel:
                                break
                            counter += 1
                        channel_dict[category][channel_name + "_" + str(counter)] = channel

                legacy_converter_dict[category][channel.rstrip("\n")] = channel_name
                # channel_dict[category].append()
    save_channel_dict(channel_dict)
    save_legacy_converter_dict(legacy_converter_dict)
    return channel_dict


# test area, gets reused whenever a bug exists
def _tester():
    # todo add commandline options for setting download dir, config dir, and a test option to show where it's looking and if it's the correct directory
    print("tester")




if __name__ == '__main__':
    main()
    #_tester()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
