import json
import os
import pickle
from collections import defaultdict
from yt_dlp import YoutubeDL

config_directory = os.getcwd() + "/configs"
download_dir = f"{os.path.expanduser('~')}/Videos/"
already_watched = {}
ignored = {}
broken_videos: dict[str, list] = {}
keywords_to_skip: dict[str, list] = {}
channels = {}
shorts_allowed = []
word_probabilities = {}
checked_titles = {}


def read_file(file_name):
    # open the file and read its lines into an array
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines


def save_ignored():
    with open(config_directory + '/ignored.json', 'w', encoding='utf-8') as outfile:
        json.dump(ignored, outfile, indent=4)


def save_downloaded_list():
    with open(config_directory + '/watched.json', 'w', encoding='utf-8') as outfile:
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
        f = open(config_directory + "/ignored.json", encoding='utf-8')
        global ignored
        ignored = json.load(f)
    except:
        ignored = {}
    pass


def read_already_watched():
    try:
        f = open(config_directory + "/watched.json", encoding='utf-8')
        global already_watched
        already_watched = json.load(f)
    except:
        already_watched = {}


def save_word_probabilities():
    tmp = dict(word_probabilities)
    with open(config_directory + '/word_probabilities.json', 'w') as f:
        json.dump(tmp, f)


def get_word_probabilities():
    return word_probabilities


def read_word_probabilities():
    try:
        with open(config_directory + '/word_probabilities.json', 'r') as f:
            data = json.load(f)
        global word_probabilities
        tmp = data
        word_probabilities = defaultdict(lambda: {True: 0.5, False: 0.5})
        for word, probabilities in tmp.items():
            word_probabilities[word].update(probabilities)
    except:
        word_probabilities = defaultdict(lambda: {True: 0.5, False: 0.5})


def get_already_watched():
    return already_watched


def get_ignored():
    return ignored


def read_not_working_videos():
    try:
        f = open(config_directory + "/broken.json", encoding='utf-8')
        global broken_videos
        broken_videos = json.load(f)
    except:
        broken_videos = {}


def get_broken_videos():
    return broken_videos


def save_broken_videos():
    with open(config_directory + '/broken.json', 'w', encoding='utf-8') as outfile:
        json.dump(broken_videos, outfile, indent=4)


def read_keywords_to_skip():
    try:
        f = open(config_directory + "/skip.json", encoding='utf-8')
        global keywords_to_skip
        keywords_to_skip = json.load(f)
    except:
        keywords_to_skip = {}


def get_keywords_to_skip():
    return keywords_to_skip


def save_channel_dict(channel_dict):
    with open(config_directory + '/channels.json', 'w', encoding='utf-8') as outfile:
        json.dump(channel_dict, outfile, indent=4)


def read_channel_dict():
    try:
        f = open(config_directory + "/channels.json", encoding='utf-8')
        global channels
        channels = json.load(f)
    except:
        channels = {}
    return channels


def read_legacy_channel_converter_dict_lists():
    try:
        f = open(config_directory + "/legacy_converter_dict.json", encoding='utf-8')
        global channels
        legacy_channels = json.load(f)
    except:
        legacy_channels = {}
    return legacy_channels


def save_legacy_converter_dict(legacy):
    with open(config_directory + '/legacy_converter_dict.json', 'w', encoding='utf-8') as outfile:
        json.dump(legacy, outfile, indent=4)


def create_channels_from_new_format(channel_dict: dict[str, dict[str, str]]):
    if not os.path.exists("./categories"):
        return channel_dict
    for file in os.listdir("./categories"):
        if file.rstrip(".json") not in channel_dict:
            channel_dict[file.rstrip(".json")] = {}
        try:
            f = open("categories/" + file)
            tmp = json.load(f)
        except:
            tmp = {}

        """
        channeldict{
        category{
            "channel" : "url"
        }
        }
        """

        for channel in tmp:
            temp: dict[str, str] = get_channel_dict(tmp[channel])
            uploader = list(temp.keys())[0]
            uploader_id = temp[uploader]
            if uploader not in channel_dict[file.rstrip(".json")]:
                channel_dict[file.rstrip(".json")][uploader] = uploader_id
            else:
                if channel_dict[file.rstrip(".json")][uploader] != uploader_id:
                    count = 0
                    while uploader + "_" + str(count) in channel_dict[file.rstrip(".json")]:
                        if channel_dict[file.rstrip(".json")][uploader + "_" + str(count)] == uploader_id:
                            break
                        count += 1
                    channel_dict[file.rstrip(".json")][uploader + "_" + str(count)] = uploader_id

    save_channel_dict(channel_dict)
    return channel_dict


def get_channel_dict(channel_link: str):
    with YoutubeDL({"quiet": "true"}) as ydl:
        test = ydl.extract_info(channel_link, download=False)

    return {str(test['uploader']): str(test['channel_id'])}


def read_shorts_allowed():
    try:
        f = open(config_directory + "/short_creators.json", encoding='utf-8')
        global shorts_allowed
        shorts_allowed = json.load(f)
    except:
        shorts_allowed = {}


def read_config_files():
    read_word_probabilities()
    read_already_watched()
    read_ignored()
    read_not_working_videos()
    read_keywords_to_skip()
    read_shorts_allowed()
    read_checked_titles()


def get_shorts_allowed():
    return shorts_allowed


def simulate_directories(new_download_dir, new_config_directory):
    if new_download_dir is not None:
        #new_download_dir = os.path.normpath(new_download_dir)
        print(new_download_dir)
        os.chdir(new_download_dir)
        print(os.getcwd())
        print(os.listdir())
    if new_config_directory is not None:
        #new_config_directory = os.path.normpath(new_config_directory)
        print(new_config_directory)
        os.chdir(new_config_directory)
        print(os.getcwd())
        print(os.listdir())


def set_directories(new_download_directory, new_config_directory, simulate):
    global download_dir
    global config_directory
    if simulate is True:
        simulate_directories(new_download_directory, new_config_directory)
        return False

    if new_download_directory is not None:
        download_dir = new_download_directory

    if new_config_directory is not None:
        config_directory = new_config_directory

    return True


def get_download_dir():
    return download_dir


def get_checked_titles():
    return checked_titles

def save_checked_titles():
    with open(config_directory + '/checked_titles.json', 'w', encoding='utf-8') as outfile:
        json.dump(checked_titles, outfile, indent=4)


def read_checked_titles():
    try:
        f = open(config_directory + "/checked_titles.json", encoding='utf-8')
        global checked_titles
        checked_titles = json.load(f)
    except:
        checked_titles = {}
    return checked_titles
