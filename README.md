# YouTube_rss_reader

reads a list of YouTube channels (by channel ids or linkx) and downloads any new video from said channels

## How to use

### Commandline options

There are three (3) options for commandline variables:

1. --config_dir="config_directory_path"
2. --download_dir="download_directory_path". This excludes a ./Youtube path which will be created if it doesn't exist
3. --simulate. Simulate prints your chosen directories and what's in them before exiting. Use this any time you change the paths! 

### for new users

- create one or more .json files in the categories directory in the following format:

````json
{
  "channel name": "link to channel or video",
  "another channel name": "another link"
}
````

- you can use either a link to a channel, or a video by the specific creator.
    - Use a video to reduce runtime by 10 fold
- run the program
- you'll find your videos under [your user directory]/Videos/Youtube/category/uploader where each json file is its own
  category eg. Gaming.json -> a folder called Gaming
- to get the newest videos, rerun this program, and it'll only download the new videos (not in)

### for returning users

- channels was changed recently to not include lists, either manually rewrite it, or just re-add from legacy/new
  categories

- rename your categories directory to legacy_categories (assuming you used the .txt version)
- run the program once
- the program will rename the legacy_categories directory to already_imported_categories
- you may now delete the already_imported_categories directory
- for adding new channels: see [new users](#for-new-users)

## Information

### config information

#### short_creators.json

a list of the names of youtubers whom you want to download shorts for. ex:

````json
{
  "short_creators": [
    "peter parker plays"
  ]
}
````

will allow you to download shorts uploaded by peter parker plays

please do note that the names are case-sensitive.

#### broken.json

A dict containing all videos that can't be downloaded (excluding premieres that aren't live yet and streams)
format:

````json
{
  "regionlocked": [
    "link"
  ],
  "Postprocessing": [
    "link",
    "link"
  ],
  "membersonly": [
    "link"
  ],
  "removed": [
    "link"
  ]
}
````

#### channels.json

A dict containing each category, channel name, and channel id:

````json
{
  "category 1": {
    "channel name": "channel id",
    "channel two": "channel id two"
  },
  "category 2": {
    "channel name": "channel id"
  }
}
````

I don't recommend editing this unless you know what you're doing

### skip.json

A dict of category, user and keyword list.
any video from the user which has one of the keywords in the list will be skipped
with extra choice of banning all words or all words in a specific category

ex:

````json
{
  "skip_in_all_categories": [],
  "skip_categories": {
    "Gaming": {
      "skip_in_this_category": [],
      "Moonbo": [
        "LIVE"
      ]
    }
  }
}
````

will not download any video posted by Moonbo that contains the word Live

an option to skip all videos containing a keyword will be added eventually

#### ignored.json

A dict of video titles that were skipped for being shorts

````json
{
  "title": 1,
  "title 2": 1
}
````

this could be converted to a list later

#### legacy_converter_dict.json

A dict used to convert the legacy categories to the new version, it can be deleted and is mostly there as a log

#### watched.json

A dict describing which files have already been downloaded:

````json
{
  "channel name": {
    "title": 1,
    "title 2": 1
  }
}
````

just used for logging and stopping re-downloading files

to re-download title 2, remove it and if it's the last line before a closing bracket, remove the comma above, ex:

````json
{
  "channel name": {
    "title": 1
  }
}
````

### Requests for additional features

- add an issue
- or make a pull request

### Downloaded videos

a json file containing the downloaded videos is created if it doesn't already exist. if you delete this file or run the
program in another directory it'll recreate an empty version of the file.
The format of the json file describing downloaded videos is:

```json
{
  "Creator": {
    "first_video": 1,
    "second_video": 1
  },
  "Creator_2": {
    "first video": 1
  }
}
```

## Warnings

on first run, this will download the last 7 or so videos of each creator. after that, it'll only download new ones
unless you add a new creator in which case the last 7 videos from the new creator will be downloaded as well.   
this is a knowing choice and will likely not change (although an added option to only download the absolute newest might
be added at a later date)  
IF you download two different videos with the same name, from the same creator (extremely unlikely) the second video
will have _0 added to the back
On occasion, it seems to leave partial downloads, but this might be from starting and stopping. if so, you can just
delete them

## Requirements

Python 3.6 or higher  
pip  
all the requirements in the requirements.txt file

ffmpeg installed in your os

## Installation

- clone this repository
- install the requirements (pip install -r requirements.txt)

## How to report bugs

- create an issue on this repository
- if the problem is related to a specific video, please include the video's url in the issue
- if the problem is related to a specific channel, please include the channel's url in the issue
- if the problem is not related to a specific video or channel, please include the error message in the issue

## Feature requests

- create a pull-request if you've written it already
- or create an issue otherwise

## Current state of project

seemingly working correctly, should handle most video titles correctly.
if a video fails, it's added to a list of broken videos and ignored. same with shorts as of now.

### Todo:

- preferably a reduction in calls to sponsorblock (will likely be left as is for now)
- add the option to turn off rate-limiting as well as to set times for rate limiting
