import json
import os

config_directory = os.getcwd() + "/configs"
already_watched = {}
ignored = {}
broken_videos: dict[str, list] = {}
keywords_to_skip: dict[str, list] = {}
channels = {}
from yt_dlp import YoutubeDL


def read_file(file_name):
    # open the file and read its lines into an array
    with open(file_name, 'r') as file:
        lines = file.readlines()
    return lines


def save_ignored():
    with open(config_directory + '/ignored.json', 'w') as outfile:
        json.dump(ignored, outfile, indent=4)


def save_downloaded_list():
    with open(config_directory + '/watched.json', 'w') as outfile:
        json.dump(already_watched, outfile, indent=4)


def read_legacy_channel_lists():
    channel_file_dict = {}
    if not os.path.exists("legacy_categories"):
        return channel_file_dict
    for channel_file in os.listdir("legacy_categories"):
        channel_file_dict[channel_file.rstrip(".txt")] = read_file("legacy_categories/" + channel_file.strip())
    os.rename("legacy_categories", "already_imported_categories")
    return channel_file_dict


def read_ignored():
    try:
        f = open(config_directory + "/ignored.json")
        global ignored
        ignored = json.load(f)
    except:
        ignored = {}
    pass


def read_already_watched():
    try:
        f = open(config_directory + "/watched.json")
        global already_watched
        already_watched = json.load(f)
    except:
        already_watched = {}


def get_already_watched():
    return already_watched


def get_ignored():
    return ignored


def read_not_working_videos():
    try:
        f = open(config_directory + "/broken.json")
        global broken_videos
        broken_videos = json.load(f)
    except:
        broken_videos = {}


def get_broken_videos():
    return broken_videos


def save_broken_videos():
    with open(config_directory + '/broken.json', 'w') as outfile:
        json.dump(broken_videos, outfile, indent=4)


def read_keywords_to_skip():
    try:
        f = open(config_directory + "/skip.json")
        global keywords_to_skip
        keywords_to_skip = json.load(f)
    except:
        keywords_to_skip = {}


def get_keywords_to_skip():
    return keywords_to_skip


def save_channel_dict(channel_dict):
    with open(config_directory + '/channels.json', 'w') as outfile:
        json.dump(channel_dict, outfile, indent=4)


def read_channel_dict():
    try:
        f = open(config_directory + "/channels.json")
        global channels
        channels = json.load(f)
    except:
        channels = {}
    return channels


def read_legacy_channel_converter_dict_lists():
    try:
        f = open(config_directory + "/legacy_converter_dict.json")
        global channels
        legacy_channels = json.load(f)
    except:
        legacy_channels = {}
    return legacy_channels


def save_legacy_converter_dict(legacy):
    with open(config_directory + '/legacy_converter_dict.json', 'w') as outfile:
        json.dump(legacy, outfile, indent=4)


def create_channels_from_new_format(channel_dict: dict[str, list[dict[str, str]]]):
    for file in os.listdir("./categories"):
        if file.rstrip(".json") not in channel_dict:
            channel_dict[file.rstrip(".json")] = []
        try:

            f = open(os.getcwd() + "/categories/" + file)

            tmp = json.load(f)
        except:
            tmp = {}
        for channel in tmp:
            if channel not in channel_dict[file.rstrip(".json")]:
                channel_dict[file.rstrip(".json")].append({channel: get_channel_id(tmp[channel])})
    return channel_dict


def get_channel_id(channel_link: str):
    with YoutubeDL({"quiet": "true"}) as ydl:
        test = ydl.extract_info(channel_link, download=False)

    return test['channel_id']
