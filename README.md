# YouTube_rss_reader
reads a list of YouTube channels (by channel ids) and downloads any new video from said channels

## How to use

- create one or more text files (.txt) in the categories directory
- in these files, add each channel's id (as found here https://commentpicker.com/youtube-channel-id.php for example) on its own individual line
- run the program.
- you'll find your videos under [your user directory]/Videos/Youtube/category/uploader where each text file is its own category eg. Gaming.txt -> a folder called Gaming
- to get the newest videos, rerun this program, and it'll only download the new videos (not in)
 

## Information

### Requests for additional features

- add an issue
- or make a pull request

### Example files

example files can be found in the Examples directory

### Downloaded videos

a json file containing the downloaded videos is created if it doesn't already exist. if you delete this file or run the program in another directory it'll recreate an empty version of the file.
The format of the json file describing downloaded videos is:
```json
{
  "Creator" : {
    "first_video" : 1,
    "second_video" : 1
  },
  "Creator_2" : {
    "first video" : 1
  }
}
```

### How to get a channel id

- go to a video of the channel you want to get the id of
- copy the url
- insert the url into the youtube channel url to id converter box here: https://commentpicker.com/youtube-channel-id.php
- copy the id from the box below the converter box
- paste the id into the text file
- repeat for each channel you want to add

the box to insert the url into:
![url_box.png](images%2Furl_box.png)
the box to copy the id from:
![id_box.png](images%2Fid_box.png)


## Warnings

on first run, this will download the last 7 or so videos of each creator. after that, it'll only download new ones unless you add a new creator in which case the last 7 videos from the new creator will be downloaded as well.
this is a knowing choice and will likely not change (although an added option to only download the absolute newest might be added at a later date)
IF you download two different videos with the same name, from the same creator (extremely unlikely) something might go wrong
 
## Requirements
Python 3.6 or higher
pip
all the requirements in the requirements.txt file

## Installation

- clone this repository
- install the requirements

## How to report bugs

- create an issue on this repository
- if the problem is related to a specific video, please include the video's url in the issue
- if the problem is related to a specific channel, please include the channel's url in the issue
- if the problem is not related to a specific video or channel, please include the error message in the issue

## Current state of project

seemingly working correctly, seems to handle most video titles correctly. 

### Todo:

- refactoring of comments
- refactoring of methods and prettifying
- preferably a reduction in calls to sponsorblock (will likely be left as is for now)
- add options that allow the user to configure the common options
- fix the time based download speed option (and add that as an option to the user)