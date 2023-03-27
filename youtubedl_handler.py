import os
import pathlib
import re
import shutil
from datetime import time, datetime
from typing import Dict, Any

from yt_dlp import YoutubeDL

from file_handler import get_already_watched, get_ignored, save_downloaded_list, save_ignored, get_broken_videos, save_broken_videos
from sponsorblock_handler import normalize, cut_sponsored_segments


# tmp


def is_in_fail_categories(link):
    broken_videos = get_broken_videos()
    for category in broken_videos:
        if link in broken_videos[category]:
            return True
    return False


def add_to_fail_category(error: Exception, entry):
    broken_videos = get_broken_videos()
    if "ERROR: Postprocessing" in error.args[0]:
        key = "Postprocessing"
    elif "Video unavailable. The uploader has not made this video available in your country" in error.args[0]:
        key = "regionlocked"
    else:
        print(error)
        raise NotImplementedError
    if key not in broken_videos:
        broken_videos[key] = []
    broken_videos[key].append(entry['link'])
    save_broken_videos()


def download_videos(entry):
    title_key = entry['title']
    author_key = entry['author']
    # if the video is less than 60 seconds long, skip it
    # this is because youtube added shorts, and they are just bad in 90% of cases
    ignored = get_ignored()
    already_watched = get_already_watched()
    if is_in_fail_categories(entry['link']):
        return
    if title_key in ignored:
        return
    if author_key not in already_watched:
        already_watched[author_key] = {}
    # todo add skip keywords
    if title_key not in already_watched[author_key]:
        # todo add option to add country blocked videos to ignored
        with YoutubeDL({"quiet": "true"}) as ydl:
            try:
                test = ydl.extract_info(entry['link'], download=False)
                title = test['title']
                author = test['uploader']

                # todo make this default but turnoff-able
                # this is actually covered by an option in ydl opts but this way we don't need to do a poll over internet
                if test['duration'] <= 60:
                    print(f"{entry['title']} is a short, skipping")
                    ignored[title_key] = 1
                    return
            except Exception as error:
                print("failed download:" + entry['title'] + " " + entry['link'])
                add_to_fail_category(error, entry)
                return
        if pathlib.Path(author).is_dir() is False:
            pathlib.Path(author).mkdir(parents=True, exist_ok=True)
        os.chdir(author)

        title = normalize(title)
        new_title = re.sub("_", " ", title)
        # this is only for debugging
        old_title = title
        ydl_opts = setup_downloader_options()
        print(f"downloading {new_title} by {author}")
        with YoutubeDL(ydl_opts) as ydl:
            try:
                os.mkdir("tmp")
                os.chdir("tmp")
                ydl.download([entry['link']])
            except Exception as e:
                os.chdir("../")
                shutil.rmtree("./tmp")
                os.chdir("../")
                add_to_fail_category(e, entry)
                print("failed download:" + entry['title'] + " " + entry['link'])
                return

        link = entry['link']
        actual_file = get_file_name(entry, link)
        cut_sponsored_segments(actual_file, entry['link'])

        os.rename(actual_file, new_title + ".webm")
        shutil.copy(new_title + ".webm", "../" + new_title + ".webm")
        print(os.listdir())
        os.chdir("../")
        os.rmdir("tmp")
        already_watched[author][title_key] = 1
        os.chdir("..")
        print("New video from " + author + ": " + new_title + " has been downloaded")
    save_downloaded_list()
    save_ignored()


def get_file_name(link, title):
    files = os.listdir(".")
    names = title.split("_")
    name_combination = ""
    for name in names:
        tmp = files
        files = list(filter(lambda x: name in x and x.endswith('.webm'), files))
        if len(files) == 0:
            files = tmp

        if len(files) == 1:
            break
        if len(files) == 0:
            raise FileNotFoundError("something went wrong, please create an issue with the link: " + link['link'])
        name_combination += "_"
    actual_file = files[0]
    return actual_file


def get_rate():
    begin_time: time = time(6, 0)
    end_time: time = time(23, 0)
    rate = 10000000
    alternative_rate = 9999999999999999999999999999999999
    check_time = datetime.now().time()
    if begin_time < end_time:
        if begin_time <= check_time <= end_time:
            return rate
    else:  # crosses midnight
        if check_time >= begin_time or check_time <= end_time:
            return rate
    return alternative_rate


def setup_downloader_options():
    rate = get_rate()
    ydl_opts = {}
    ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
    ydl_opts['format'] = 'bestvideo+bestaudio/best'
    ydl_opts['merge_output_format'] = 'webm'
    ydl_opts['ratelimit'] = rate
    ydl_opts['restrictfilenames'] = 'true'
    ydl_opts['match_filter'] = longer_than_a_minute
    ydl_opts['quiet'] = 'true'
    return ydl_opts


def longer_than_a_minute(info, *, incomplete):
    # todo: add a possibility to set specific youtubers to short creators (basically tik-tok) maybe shorts_category_name? and then put them in their own category or the same as the non-shorts?? options.
    """Download only videos longer than a minute (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration < 60:  # <= after fix of ...
        return 'The video is too short'
