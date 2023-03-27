import json
import os

config_directory = os.getcwd()
already_watched = {}
ignored = {}
broken_videos: dict[str, list] = {}




def read_file(file_name):
    # open the file and read its lines into an array
    with open(file_name, 'r') as file:
        lines = file.readlines()
    # return the array
    return lines


def save_ignored():
    with open(config_directory + '/ignored.json', 'w') as outfile:
        json.dump(ignored, outfile)


def save_downloaded_list():
    with open(config_directory + '/watched.json', 'w') as outfile:
        json.dump(already_watched, outfile)


def read_channel_lists():
    channel_file_dict = {}
    for channel_file in os.listdir("categories"):
        channel_file_dict[channel_file.strip()] = read_file("categories/" + channel_file.strip())
    return channel_file_dict


def read_ignored():
    try:
        f = open("ignored.json")
        global ignored
        ignored = json.load(f)
    except:
        ignored = {}
    pass


def read_already_watched():
    try:
        f = open("watched.json")
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
        f = open("broken.json")
        global broken_videos
        broken_videos = json.load(f)
    except:
        broken_videos = {}

def get_broken_videos():
    return broken_videos

def save_broken_videos():
    with open(config_directory + '/broken.json', 'w') as outfile:
        json.dump(broken_videos, outfile)
