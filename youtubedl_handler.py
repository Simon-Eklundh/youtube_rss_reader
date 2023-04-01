import os
import pathlib
import re
from datetime import time, datetime

from unidecode import unidecode
from yt_dlp import YoutubeDL

from file_handler import get_already_watched, get_ignored, save_downloaded_list, save_ignored, get_broken_videos, \
    save_broken_videos, get_keywords_to_skip
from sponsorblock_handler import normalize, cut_sponsored_segments


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
    elif "Join this channel to get access to members-only content like this video, and other exclusive perks." in \
            error.args[0]:
        key = "membersonly"
    elif "This live event will begin" in error.args[0]:
        return
    elif "Video unavailable. This video is not available" in error.args[0]:
        key = "removed"
    else:
        print(error)
        raise NotImplementedError
    if key not in broken_videos:
        broken_videos[key] = []
    broken_videos[key].append(entry['link'])
    save_broken_videos()


def get_new_title(new_title):
    count = 0
    tmp = new_title + "_" + str(count) + ".webm"
    while tmp in os.listdir():
        count += 1
        tmp = new_title + "_" + str(count) + ".webm"
    return tmp


def download_videos(entry):
    title_key = entry['title']
    author_key = entry['author']
    # if the video is less than 60 seconds long, skip it
    # this is because youtube added shorts, and they are just bad in 90% of cases
    ignored = get_ignored()
    already_watched = get_already_watched()
    keywords_to_skip = get_keywords_to_skip()
    if is_in_fail_categories(entry['link']):
        return
    if title_key in ignored:
        return
    if author_key in keywords_to_skip:
        for keyword in keywords_to_skip[author_key]:
            if keyword in title_key:
                print("keyword: " + keyword + " is in " + title_key + " by " + entry['author'] + ", skipping")
                return
    if author_key not in already_watched:
        already_watched[author_key] = {}

    if title_key not in already_watched[author_key]:
        print(f"Checking {title_key} by {author_key}")
        with YoutubeDL({"quiet": "true"}) as ydl:
            try:
                test = ydl.extract_info(entry['link'], download=False)
                title = test['title']
                author = test['uploader']
                if "live_status" in test and test['live_status'] == "is_live":
                    print("livestream is still live")
                    return
                # todo make this default but turnoff-able
                # this is actually covered by an option in ydl opts but this way we don't need to do a poll over internet
                if 'duration' in test and test['duration'] <= 60:
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
        ydl_opts = setup_downloader_options()

        with YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Downloading {title_key} by {author_key}")
                ydl.download([entry['link']])
                print(f"Downloaded {title_key} by {author_key}")
            except Exception as e:

                os.chdir("../")
                add_to_fail_category(e, entry)
                print("Failed download:" + entry['title'] + " " + entry['link'])
                return

        link = entry['link']

        actual_file = get_file_name(title_key, link)
        tmp = re.sub(" ", "_", actual_file)
        tmp = unidecode(tmp)
        os.rename(actual_file, tmp)
        print(f"cutting {title_key} by {author_key}")
        cut_sponsored_segments(re.sub("(.webm)", "", tmp), entry['link'])
        print(f"done cutting {title_key} by {author_key}")
        new_title = actual_file
        if actual_file in os.listdir():
            new_title = get_new_title(actual_file)
        os.rename(tmp, new_title + ".webm")
        already_watched[author][title_key] = 1
        os.chdir("..")
        print("New video from " + author + ": " + actual_file + " has been downloaded and cut")
    save_downloaded_list()
    save_ignored()


def get_file_name(title, link):
    files = os.listdir(".")
    names = title.split(" ")
    for file in files:
        if file == title + ".webm":
            return file

    for name in names:
        tmp = files
        files = list(filter(lambda x: name in x and x.endswith('.webm'), files))
        if len(files) == 0:
            files = tmp

        if len(files) == 1:
            break
        if len(files) == 0:
            raise FileNotFoundError("something went wrong, please create an issue with the link: " + link['link'])
    if len(files) > 1:
        files = list(filter(lambda x: len(x) == len(title + ".webm"), files))
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
    ydl_opts['match_filter'] = longer_than_a_minute
    ydl_opts['quiet'] = 'true'
    return ydl_opts


def longer_than_a_minute(info, *, incomplete):
    # todo: add a possibility to set specific youtubers to short creators (basically tik-tok) maybe shorts_category_name? and then put them in their own category or the same as the non-shorts?? options.
    """Download only videos longer than a minute (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration < 60:  # <= after fix of ...
        return 'The video is too short'
