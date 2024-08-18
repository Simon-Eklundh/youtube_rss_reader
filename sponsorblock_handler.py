import fnmatch
import os

import subprocess

import sponsorblock as sb



def get_segments_to_remove(url):
    client = sb.Client()
    # get sponsor segments from sponsorblock (including sponsors, intro, outro and interaction reminders)
    segments = client.get_skip_segments(url, categories=["sponsor", "selfpromo", "interaction", "intro", "outro", "preview"])
    return segments


def cut_sponsored_segments(file_name, file_type, sponsorblock_segments):

    if sponsorblock_segments is None:
        return
    create_clips_of_the_parts_to_leave_in(file_name, sponsorblock_segments, file_type)

    create_clip_file_list(file_name)
    # concatenate all the clips in order into a single video
    subprocess.call(f"ffmpeg -safe 0 -y -f concat -i {file_name}_list.txt -c copy {file_name}.{file_type} ")

    for file in os.listdir():
        if file.startswith(file_name + "_"):
            os.remove(file)


def create_clip_file_list(file_name):
    files = []
    for file in os.listdir():
        if file.startswith(file_name + "_"):
            files.append(file)
    # sorting is actually unnecessary but it's for good measure
    files.sort(key=file_sorter)
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


def rename_clips_in_order(file_name):
    files = []
    clip_index = 0
    file_dict = {}
    for file in os.listdir():
        if file.startswith(file_name + "_") and file.endswith(".webm"):
            files.append(file)
    files.sort(key=file_sorter)

    for file in files:
        new_file_name = file_name + "_" + str(clip_index) + ".webm"
        clip_index += 1
        file_dict[new_file_name] = file
    for file in file_dict:
        os.rename(file_dict[file], file)


# remove any duplicate segments to make sure cutting works perfectly (wouldn't work if I change which segment types are allowed)
def fix_segments(segments):
    new_segments = []
    for segment in segments:
        skip = False
        for seg in new_segments:
            if segment.start > seg.start and seg.end > segment.end:
                skip = True
                break

            if seg.start < segment.start < seg.end < segment.end:
                seg.end = segment.end
                skip = True
        if not skip:
            new_segments.append(segment)

    return new_segments


def create_clips_of_the_parts_to_leave_in(file_name, segments, file_type):
    current_start: float = 0.0
    os.rename(file_name + "." + file_type, file_name + "_0." + file_type)
    clip_index = 1
    segments = fix_segments(segments)
    for segment in segments:
        start: float = segment.start
        end: float = segment.end

        subprocess.call(
            f"""ffmpeg -y -ss {current_start} -to {start} -i "{file_name}_0.{file_type}" -c copy "{file_name}_{clip_index}.{file_type}" """
        )
        clip_index += 1
        current_start: float = end
    # No end time to get the final part of the video
    subprocess.call(
        f"""ffmpeg -y -ss {current_start} -i "{file_name}_0.{file_type}" -c copy "{file_name}_{clip_index}.{file_type}" """
    )
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, file_name + "_[^1-9]." + file_type):
            os.remove(file_name + "_0." + file_type)
            return
