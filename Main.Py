import json
import pathlib
import re
import subprocess
from datetime import datetime
from unidecode import unidecode
import feedparser
import sponsorblock as sb
from moviepy.editor import *
from sponsorblock import Segment
from yt_dlp import YoutubeDL

already_watched = {}

start_directory = ""


def read_file(file_name):
    # open the file and read its lines into an array
    with open(file_name, 'r') as file:
        lines = file.readlines()
    # return the array
    return lines


def get_segments_to_remove(url):
    client = sb.Client()
    # get sponsor segments from sponsorblock (including sponsors, intro, outro and interaction reminders)
    segments = client.get_skip_segments(url)

    return segments


def cut_sponsored_segments(file_name, url):
    # this uses an api call which returns a 404 if the video isn't in sponsorblock. if it returns an error, we don't cut
    try:
        segments: list[Segment] = get_segments_to_remove(url)
    except:
        return

    create_clips_of_the_parts_to_leave_in(file_name, segments)

    # rename_the clips despite it likely being unnecessary
    rename_clips_in_order(file_name)

    create_clip_file_list(file_name)
    # concatenate all the clips in order into a single video
    subprocess.Popen(f"ffmpeg -safe 0 -y -f concat -i {file_name + '_list.txt'} -c copy {file_name + '.mp4'}").wait()

    os.remove(file_name + "_list.txt")
    for file in os.listdir():
        if file.startswith(file_name+"_"):
            os.remove(file)


def create_clip_file_list(file_name):
    files = []
    for file in os.listdir():
        if file.startswith(file_name + "_"):
            files.append(file)
    # sorting is actually unnecessary but it's for good measure
    files.sort()
    # open file_name_list.txt and write the list of files to it
    with open(file_name + "_list.txt", 'a') as file:
        for f in files:
            file.write(f"file '{f}'\n")


# because python sorts files like this: file_1.mp4 file_10.mp4 file_2.mp4, we force python to sort by int
def fileSorter(e:str):
    out = e.split("_")
    key: int = int(out[len(out) - 1].split(".")[0])
    return key

def rename_clips_in_order(file_name):

    files = []
    clip_index = 0
    file_dict = {}
    for file in os.listdir():
        if file.startswith(file_name + "_") and file.endswith(".mp4"):
            files.append(file)
    files.sort(key=fileSorter)

    for file in files:
        new_file_name = file_name + "_" + str(clip_index) + ".mp4"
        clip_index += 1
        file_dict[new_file_name] = file
    for file in file_dict:
        os.rename(file_dict[file], file)




def create_clips_of_the_parts_to_leave_in(file_name, segments):
    current_start = "00:00:00"
    clip_index = 0
    for segment in segments:
        start = segment.start
        end = segment.end
        subprocess.Popen(
            f"ffmpeg -y -ss {current_start} -to {start} -i {file_name}.mp4 -c copy {file_name}_{clip_index}.mp4"
        ).wait()
        current_start = end
        clip_index += 1


def download_and_sponsorblock_videos(channels, category):
    # for each channel in the list of channels, read rss feed and print the title of the first item
    # if category is not an existing folder, create it
    if pathlib.Path(category).is_dir() is False:
        pathlib.Path(category.strip(".txt")).mkdir(parents=True, exist_ok=True)
    os.chdir(category)
    for channel in channels:

        channel_rss_feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel)
        # for each rss feed item, check if it is already in the already_watched dictionary
        for entry in channel_rss_feed['entries']:
            download_videos(entry)

    os.chdir("../")


def download_videos(entry):
    global already_watched

    title = re.sub(":",'_-',entry['title'])
    author = re.sub(r'[^\w_.-]', '_', entry['author'])
    title = re.sub(r'[^\w_.%-]', '_', title).rstrip("_").lstrip("_")

    title = unidecode(title                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 )
    while title.__contains__("__"):
        title = re.sub(r'(__)', '_', title)
    new_title = re.sub(r'%', '',title)
    while new_title.__contains__("_-_"):
        new_title = re.sub(r'-', '_', new_title)
    while new_title.__contains__("__"):
        new_title = re.sub(r'(__)', '_', new_title)
    new_title = re.sub(r'[_]'," ", new_title)

    if author not in already_watched:
        already_watched[author] = {}
    if new_title not in already_watched[author]:
        ydl_opts = setup_downloader_options()
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([entry['link']])
            except:
                return

        # rename downloaded file to remove all disallowed characters

        cut_sponsored_segments(title, entry['link'])
        os.rename(title + ".mp4", new_title + ".mp4")
        already_watched[author][new_title] = 1
        print("New video from " + author + ": " + new_title + " has been downloaded")
    save_downloaded_list()


def setup_downloader_options():
    now = datetime.now()
    #
    current_time = now.strftime("%H:%M:%S")
    if "23:00:00" < current_time < "06:00:00":
        rate = 10000000000000000
    else:
        rate = 10000000
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'ratelimit': rate,
        'restrictfilenames': 'true',
        'match_filter': longer_than_a_minute,
    }
    return ydl_opts


def longer_than_a_minute(info, *, incomplete):
    """Download only videos longer than a minute (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration < 60:
        return 'The video is too short'


def main():
    global start_directory
    start_directory = os.getcwd()
    get_already_watched()

    channel_file_dict = read_channel_lists()

    download_dir = f"{os.path.expanduser('~')}/Videos/Youtube"
    os.chdir(download_dir)

    # for each entry in channel_file_dict
    for channel in channel_file_dict:
        download_and_sponsorblock_videos(channel_file_dict[channel], channel.strip(".txt"))




def get_already_watched():
    try:
        f = open("watched.json")
        global already_watched
        already_watched = json.load(f)
    except:
        already_watched = {}



def save_downloaded_list():
    global already_watched
    with open(start_directory+'/watched.json', 'w') as outfile:
        json.dump(already_watched, outfile)


def read_channel_lists():
    channel_file_dict = {}
    for channel_file in os.listdir("categories"):
        channel_file_dict[channel_file.strip()] = read_file("categories/" + channel_file.strip())
    return channel_file_dict




if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
