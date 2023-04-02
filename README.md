# YouTube_rss_reader
reads a list of YouTube channels (by channel ids or linkx) and downloads any new video from said channels

## How to use

### for new users

- create one or more .json files in the categories directory in the following format:
````json
{
  "channel name" : "link to channel or video",
  "another channel name" : "another link"
}
````
- you can use either a link to a channel, or a video by the specific creator. 
  - Use a video to reduce runtime by 10 fold
- run the program
- you'll find your videos under [your user directory]/Videos/Youtube/category/uploader where each json file is its own category eg. Gaming.json -> a folder called Gaming
- to get the newest videos, rerun this program, and it'll only download the new videos (not in)

### for returning users
- rename your categories directory to legacy_categories (assuming you used the .txt version)
- run the program once
- the program will rename the legacy_categories directory to already_imported_categories
- you may now delete the already_imported_categories directory
- for adding new channels: see [new users](#for-new-users)


## Information

### config information

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
  "category 1" : [
    {
      "channel name" : "channel id"
    }
  ],
  "category 2" : [
    {
      "channel name" : "channel id"
    }
  ]
}
````
I don't recommend editing this unless you know what you're doing

#### ignored.json

A dict of video titles that were skipped for being shorts

````json
{
  "title": 1,
  "title 2" : 1
}
````
this could be converted to a list later

#### legacy_converter_dict.json

A dict used to convert the legacy categories to the new version, it can be deleted and is mostly there as a log

#### watched.json

A dict describing which files have already been downloaded:

````json
{
  "channel name" : {
    "title" : 1,
    "title 2"
  }
}
````

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
IF you download two different videos with the same name, from the same creator (extremely unlikely) the second video will have _0 added to the back
 
## Requirements
Python 3.6 or higher  
pip  
all the requirements in the requirements.txt file  

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

- refactoring of comments
- refactoring of methods and prettifying
- preferably a reduction in calls to sponsorblock (will likely be left as is for now)
- add options that allow the user to configure the common options
- add the option to turn off rate-limiting as well as to set times for rate limiting
