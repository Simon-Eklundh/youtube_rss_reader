import os
import pathlib
import re
from datetime import time, datetime

from yt_dlp import YoutubeDL

from file_handler import get_already_watched, get_ignored, save_downloaded_list, save_ignored, get_broken_videos, \
    save_broken_videos, get_keywords_to_skip, get_shorts_allowed
from sponsorblock_handler import cut_sponsored_segments


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
    elif"HTTP Error 503: Service Unavailable" in error.args[0]:
        return
    elif "Video unavailable. The uploader has not made this video available in your country" in error.args[0]:
        key = "regionlocked"
    elif "Join this channel to get access to members-only content like this video, and other exclusive perks." in \
            error.args[0]:
        key = "membersonly"
    elif "This live event will begin" in error.args[0]:
        return
    elif "Premieres in" in error.args[0]:
        return
    elif "Video unavailable. This video is not available" in error.args[0]:
        key = "removed"
    else:
        print(error)
        print(error.args[0])
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


def should_skip(entry, ignored, already_watched, category):
    keywords_to_skip = get_keywords_to_skip()
    shorts_allowed = get_shorts_allowed()
    if is_in_fail_categories(entry['link']):
        return True
    if entry['title'] in ignored:
        return True
    if 'skip_categories' in keywords_to_skip and category in keywords_to_skip['skip_categories']:
        if entry['author'] in keywords_to_skip['skip_categories'][category]:

            for keyword in keywords_to_skip['skip_categories'][category][entry['author']]:
                if keyword in entry['title']:
                    print("category and author based keyword: " + keyword + " is in " + entry['title'] + " by " + entry[
                        'author'] + ", skipping")
                    ignored[entry['title']] = 1
                    return True
        if 'skip_in_this_category' in keywords_to_skip['skip_categories'][category]:
            for keyword in keywords_to_skip['skip_categories'][category]['skip_in_this_category']:
                if keyword in entry['title']:
                    print("category keyword: " + keyword + " is in " + entry['title'] + " by " + entry[
                        'author'] + ", skipping")
                    ignored[entry['title']] = 1
                    return True
    if 'skip_in_all_categories' in keywords_to_skip:
        for keyword in keywords_to_skip['skip_in_all_categories']:
            if keyword in entry['title']:
                print(
                    "global keyword: " + keyword + " is in " + entry['title'] + " by " + entry['author'] + ", skipping")
                ignored[entry['title']] = 1
                return True

    if entry['author'] not in already_watched:
        already_watched[entry['author']] = {}

    if entry['title'] in already_watched[entry['author']]:
        return True
    print(f"Checking {entry['title']} by {entry['author']}")
    with YoutubeDL({"quiet": "true"}) as ydl:
        try:
            test = ydl.extract_info(str(entry['link']), download=False)
            if "live_status" in test and test['live_status'] == "is_live":
                print("livestream is still live")
                return True


            if 'duration' in test and test['duration'] <= 60:
                if entry['author'] not in shorts_allowed['short_creators']:
                    print(f"{entry['title']} is a short, skipping")
                    ignored[entry['title']] = 1
                    return True

        except Exception as error:
            print("failed download:" + entry['title'] + " " + entry['link'])
            add_to_fail_category(error, entry)
            return True

    return False


def delete_tmps():
    files = os.listdir(".")
    files = list(filter(lambda x: re.match(r".*\.f\d+\.(webm|mp4)", x) or re.match(r".*\.temp\.(webm|mp4)", x), files))
    for file in files:
        os.remove(file)



def download_videos(entry, category):
    title_key = entry['title']
    author_key = entry['author']
    # if the video is less than 60 seconds long, skip it
    # this is because youtube added shorts, and they are just bad in 90% of cases
    ignored = get_ignored()
    already_watched = get_already_watched()

    if should_skip(entry, ignored, already_watched, category):
        save_ignored()
        return

    if pathlib.Path(author_key).is_dir() is False:
        pathlib.Path(author_key).mkdir(parents=True, exist_ok=True)
    os.chdir(author_key)
    ydl_opts = setup_downloader_options(entry)

    if not download_video(author_key, entry, title_key, ydl_opts, category):
        delete_tmps()
        os.chdir("../")
        return

    actual_file = handle_video(author_key, entry, title_key)
    already_watched[author_key][title_key] = 1
    os.chdir("..")
    print("New video from " + author_key + ": " + actual_file + " has been downloaded and cut")
    save_downloaded_list()


def handle_video(author_key, entry, title_key):
    file_array = get_file(title_key, entry['link'])
    file_name = file_array[0]
    file_type = file_array[1]
    tmp = "file." + file_type
    os.rename(file_name, tmp)
    print(f"cutting {title_key} by {author_key}")
    cut_sponsored_segments(re.sub(f".{file_type}", "", tmp), entry['link'], file_type)
    print(f"done cutting {title_key} by {author_key}")
    new_title = file_name
    if file_name in os.listdir():
        new_title = get_new_title(file_name)
    os.rename(tmp, new_title)
    return file_name


def download_video(author_key, entry, title_key, ydl_opts, category):
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Downloading {title_key} by {author_key} from category {category}")

            ydl.download([entry['link']])
            print(f"Downloaded {title_key} by {author_key}")
        except Exception as e:
            add_to_fail_category(e, entry)
            print("Failed download:" + entry['title'] + " " + entry['link'])
            return False
    return True


def get_file(title, link):
    files = os.listdir(".")
    names = title.split(" ")
    for name in names:
        tmp = files
        files = list(filter(lambda x: name in x and not x.endswith(".txt"), files))
        if len(files) == 0:
            files = tmp

        if len(files) == 1:
            break
        if len(files) == 0:
            raise FileNotFoundError("something went wrong, please create an issue with the link: " + link)
    actual_file = files[0]
    file_type = actual_file.split(".")[len(actual_file.split("."))-1]
    return [actual_file, file_type]


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



def setup_downloader_options(entry):
    # todo add subtitle language options with/out auto generated?
    rate = get_rate()
    ydl_opts = {}


    ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
    ydl_opts['format'] = 'bestvideo+bestaudio/best'
    ydl_opts['ratelimit'] = rate
    ydl_opts['quiet'] = True
    ydl_opts['subtitleslangs'] = ["en"]
    ydl_opts['writesubtitles'] = True,
    ydl_opts['postprocessors'] = [
         {
             'key': 'FFmpegEmbedSubtitle'
         }

    ]

    return ydl_opts


def longer_than_a_minute(info, *, incomplete):
    """Download only videos longer than a minute (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration < 60:  # <= after fix of ...
        return 'The video is too short'
