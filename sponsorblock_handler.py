import os
import re
import subprocess

import sponsorblock as sb
from unidecode import unidecode


def get_segments_to_remove(url):
    client = sb.Client()
    # get sponsor segments from sponsorblock (including sponsors, intro, outro and interaction reminders)
    segments = client.get_skip_segments(url)
    return segments


def cut_sponsored_segments(file_name, url):
    # this uses an api call which returns a 404 if the video isn't in sponsorblock. if it returns an error, we don't cut
    # todo reduce these calls somehow (self-hosting?) left for last
    try:
        segments: list[sb.Segment] = get_segments_to_remove(url)
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
        if file.startswith(file_name + "_"):
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


# because python sorts files like this: file_1.mp4 file_10.mp4 file_2.mp4, we force python to sort by the "part number"
# in other words: sort by X where X is a number in file_X.mp4
def file_sorter(e: str):
    out = e.split("_")
    key: int = int(out[len(out) - 1].split(".")[0])
    return key


def normalize(title):
    title = re.sub("[—°]", "_", title)
    title = unidecode(title)
    title = re.sub(":", '_-', title)
    title = re.sub(r"[^\w_.%+@-]", '_', title)
    while "__" in title:
        title = re.sub(r'(__)', '_', title)
    while title.startswith("'") or title.startswith("_") or title.endswith("-") or title.endswith("_"):
        title = title.strip("_").strip("-")

    return title


def rename_clips_in_order(file_name):
    files = []
    clip_index = 0
    file_dict = {}
    for file in os.listdir():
        if file.startswith(file_name + "_") and file.endswith(".mp4"):
            files.append(file)
    files.sort(key=file_sorter)

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
