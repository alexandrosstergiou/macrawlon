<center>
  <img src="images/macralon_iconandtext.png" alt="text" width="400"/>
</center>

### (a Multi-processing Audiovisual CRAWLer collectiON)

![supported versions](https://img.shields.io/badge/python-3.x-brightgreen?style=for-the-badge&logo=python) &nbsp;  [![PyPi](https://img.shields.io/badge/pypi-yellow?style=for-the-badge&logo=pypi)](https://twitter.com/intent/tweet?text=macrawlon🍬&video&and&audio&crawler&url=https://github.com/alexandrosstergiou/macrawlon&hashtags=VideoAudioCrawler) &nbsp; ![Licence](https://img.shields.io/badge/licence-mit-gray?style=for-the-badge) &nbsp; [![Tweet](https://img.shields.io/badge/tweet-white?style=for-the-badge&logo=twitter)](https://twitter.com/intent/tweet?text=macrawlon🍬&video&and&audio&crawler&url=https://github.com/alexandrosstergiou/macrawlon&hashtags=VideoAudioCrawler)


----------------------
About
----------------------


A package for crawling and downloading YouTube videos. As multiple datasets that are introduced only provide the ids of videos without a download script, obtaining the video files may be difficult. This project aims to provide a general solution is such cases by downloading either the video or audio from ids specified by a dataset. It also aims to speed up processing though enabling multiple threads to run in parallel. The video resolution is user set in order to speed-up downloading and to limit the on-disk dataset size.

Currently only video-only or audio-only files are downloaded (the next update/version will allow to also download videos with audio).

----
Package Requirements
----
This is the list of the required packages:
- `pandas`
- `pafy`
- `ffmpeg`
- `youtube-dl`
- `tqdm`

They can all be downloaded with:
```
$ pip install pandas pafy tqdm
```

---
CSV Dataset file
---

The package assumes that the following headers are included in the `.csv` file that includes the YouTube ids:

| youtube_id | start | end (or) duration |
| ---------- | ------| ------------------|

The name of the headers do not need to match exactly but the data needs to include the id, start time end time or duration.


---
Usage
---

The main function used to download files is called `download()` as is located at the `youtube_audio_and_video_downloader.py`. You can simply call it by first importing it:
```python
from macrawlon import download
#or
from youtube_audio_and_video_downloader import download

download(
  csv_dir=my_csv_dir,
  download_dir=my_down_dir,
  modality='video',
  resolutions=my_res_list,
  id_idx = 0,
  start_idx = 1,
  end_idx = None,
  duration=10,
  workers=5
  )

```

The function takes the following arguments:

| Argument | About |
| ---- | ---- |
| `csv_dir` | directory for the dataset `.csv` file. |
| `download_dir` | directory for the location to download |
| `modality` | video modality to download, can choose `audio`, `video`, `audio-video` for separate audio and video files or `audio+video` for video files with audio. |
| `resolutions` | (optional) list of resolution qualities, with the first list elements being the preferred options. |
| `id_idx` | (optional) The column index in the csv file that contains the youtube video ids. E.g. if `0` then the first column of the csv should have the youtube video ids.|
| `start_idx` | (optional) The index for the starting location (in secs.) in the video.|
| `end_idx` | (optional) The index for the ending location (in secs.) in the video.|
| `duration` | (optional) The duration (in secs.) of the video. To be used if `end_idx` is not specified.|
| `workers` | (optional) The number of sub-processes to run.|


-------------------------
Installation through git
-------------------------

Please make sure, Git is installed in your machine:
```
$ sudo apt-get update
$ sudo apt-get install git
$ git clone https://github.com/macrawlon/macrawlon.git
$ cd macrawlon
$ pip install .
```

You can then use it as any other package installed through pip.

-------------------------
Installation through pip
-------------------------

The latest stable release is also available for download through pip
```
$ pip install macrawlon
```


-------------------------
Licence
-------------------------
MIT
