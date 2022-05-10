'''
---  I M P O R T  S T A T E M E N T S  ---
'''
# Path to ffmpeg
ffmpeg_path = '/home/astergiou/miniconda3/bin/ffmpeg' #'../bin/ffmpeg/ffmpeg'

import sys
import os
# Make sure ffmpeg is on the path so sk-video can find it
sys.path.append(os.path.dirname(ffmpeg_path))
import skvideo.io
import pandas as pd
import pafy
import subprocess as sp
import requests
from multiprocessing import Pool
import tqdm

'''
---  S T A R T  O F  F U N C T I O N  V I D E O _ D O W N L O A D E R  ---
    [About]
        Worker function that takes a single list argument containing the ffmpeg filepath, the start time
        (in seconds) of the video segment to download, the url of the video, the segment duration,
        the format of the video (mp4) and the target filepath in which the video is saved at.
    [Args]
        - inp: List containing:
            + ffmpeg filepath as a string.
            + the start time as a float/integer.
            (in seconds) of the video segment to download.
            + the url of the video as a string.
            + the segment duration as a float/integer.
            + the format that the video will be downloaded to as a string (e.g. `mp4`).
            + the filepath as a string where the video will be downloaded.
    [Returns]
        - None
'''
def video_downloader(inp):
    ffmpeg_path, ts_start, video_url, duration, video_format, video_filepath = inp
    # Download the video
    video_dl_args = [ffmpeg_path, '-n',
                    '-ss', str(ts_start),   # The beginning of the trim window
                    '-i', str(video_url),        # The video URL
                    '-t', str(duration),    # The video segment duration
                    '-f', video_format,     # The video format
                    '-framerate', '30',     # The framerate
                    '-vcodec', 'h264',      # The output encoding
                    video_filepath]         # The output filepath

    proc = sp.Popen(video_dl_args, stdout=None, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        print(stderr)

    return
'''
---  E N D  O F  F U N C T I O N  V I D E O _ D O W N L O A D E R  ---
'''



'''
---  S T A R T  O F  F U N C T I O N  A U D I O _ D O W N L O A D E R  ---
    [About]
        Worker function that takes a single list argument containing the ffmpeg filepath, the start time
        (in seconds) of the audio segment to download, the url of the video, the segment duration,
        the audio codec, and the target filepath in which the audio is saved at.
    [Args]
        - inp: List containing:
            + ffmpeg filepath as a string.
            + the start time as a float/integer.
            (in seconds) of the audio segment to download
            + the url of the video as a string.
            + the segment duration as a float/integer.
            + the codec of the audio.
            + the filepath as a string where the audio will be downloaded.
    [Returns]
        - None
'''
def audio_downloader(inp):
    ffmpeg_path, ts_start, audio_url, duration, audio_codec, audio_filepath = inp
    # Download the audio
    audio_dl_args = [ffmpeg_path, '-n',
                    '-ss', str(ts_start),    # The beginning of the trim window
                    '-i', audio_url,         # The video URL
                    '-t', str(duration),     # The duration of the segment
                    '-vn',                   # Suppress the video stream
                    '-ac', '2',              # Set the number of channels
                    '-sample_fmt', 's16',    # Specify the bit depth
                    '-acodec', audio_codec,  # Specify the output encoding
                    '-ar', '44100',          # Specify the audio sample rate
                    audio_filepath]

    proc = sp.Popen(audio_dl_args, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        print(stderr)
    return
'''
---  E N D  O F  F U N C T I O N  A U D I O _ D O W N L O A D E R  ---
'''



'''
---  S T A R T  O F  F U N C T I O N  T R Y _ V I D E O  ---
    [About]
        Function for cheching availability of a given YouTube video.
    [Args]
        - url: List for the video url to check in string format and the start/end times as floats.
    [Returns]
        - url or None: URL string of the video if the video is accessible or None if the video isn't.
'''
def try_video(url):
    v_url = url[0]
    pattern = '"playabilityStatus":{"status":"ERROR"'
    request = requests.get(v_url)
    is_True= False if pattern in request.text else True
    if not is_True:
        return ""
    return url
'''
---  S T A R T  O F  F U N C T I O N  T R Y _ V I D E O  ---
'''



'''
---  S T A R T  O F  F U N C T I O N  G E T _ V I D E O _ A U D I O _ U R L S ---
    [About]
        Function for getting the urls of video-only, audio-only or video with audio urls given
        specified resolution.
    [Args]
        - url: List containing the original video url and a list of the start/end times as floats.
    [Returns]
        - Tuple containing the original video url as a string, a list of the start/end times as floats
          and a list for the video-only, audio-only and video with audio urls at the specified resolutions.
'''
def get_video_audio_urls(url):
    try:
        video_page_url = url[0]
        # Get the direct URLs to the videos with best audio and with best video (with audio)
        video = pafy.new(video_page_url)
        names = [[v.extension,v.resolution.split('x')[-1]] for v in video.videostreams]
        resolutions = [v.resolution.split('x')[-1] for v in video.videostreams]
        resolutions = sorted(set(resolutions))
        idx = -1
        for res in res_options:
            if ['mp4',res] in names:
                idx = names.index(['mp4',res])
                break
        #assert idx!=0 -1, f'No index found, consider including one of the following available resolutions: {resolutions} at the `res_options` argument.'
        if idx==-1:
            best_video = video.getbestvideo()
        else:
            best_video = video.videostreams[idx]

        names = [[v.extension,v.resolution.split('x')[-1]] for v in video.streams]
        resolutions = [v.resolution.split('x')[-1] for v in video.streams]
        resolutions = sorted(set(resolutions))
        idx = -1
        for res in res_options:
            if ['mp4',res] in names:
                idx = names.index(['mp4',res])
                break
        #assert idx!=0 -1, f'No index found, consider including one of the following available resolutions: {resolutions} at the `res_options` argument.'
        if idx==-1:
            best_video_w_audio = video.getbest()
        else:
            best_video_w_audio = video.streams[idx]

        best_video_url = best_video.url
        best_audio = video.getbestaudio()
        best_audio_url = best_audio.url
        best_video_w_audio_url = best_video_w_audio.url

        return (url[0], url[1], [best_video_url, best_audio_url, best_video_w_audio_url])
    except Exception as e:
        print(e)
        return
    return
'''
---  E N D  O F  F U N C T I O N  G E T _ V I D E O _ A U D I O _ U R L S ---
'''



'''
---  S T A R T  O F  F U N C T I O N  D O W N L O A D ---
    [About]
        Main function for downloading video and audio YouTube videos from `.csv` files.
    [Args]
        - csv_dir: String for the directory for the dataset `.csv` file.
        - download_dir: String for the directory that the files are to be downloaded in.
        - modality: String for the video modality to download, can choose `audio`, `video`, `audio-video` for separate audio and video files or `audio+video` for video files with audio.
        - resolution: (optional) List for resolutions that videos are to be downloaded in, the first list elements being the preferred options.
        - id_idx: (optional) Integer for the column index in the `.csv` file that contains the youtube video ids. E.g. if `0` then the first column of the csv should have the youtube video ids.
        - start_idx: (optional) Integer/Float for the index for the starting location (in secs.) in the video.
        - end_idx: (optional) Integer/Float for the index for the ending location (in secs.) in the video.
        - duration: (optional) Integer/Float for the duration (in secs.) of the video. To be used if `end_idx` is not specified.
        - workers: (optional) Integer for the number of sub-processes to run.
    [Returns]
        - None
'''
def download(
  csv_dir, download_dir, modality, resolutions=['480', '360' ,'240'],
  id_idx = 0, start_idx = 1, end_idx = 2, duration=10, workers=5):

  # Set output settings
  audio_codec = 'flac'
  audio_container = 'flac'
  video_codec = 'h264'
  video_format = 'mp4'
  directory= download_dir

  global res_options
  res_options = resolutions

  # Load the AudioSet training set
  df = pd.read_csv(csv_dir)
  urls = []
  times = []

  print("\n"*3, end="")
  # Iterate over videos
  for index, row in df.iterrows():
      ytid = row[id_idx]
      ts_start = row[start_idx]
       if end_idx is not None:
           ts_end = row[end_idx]
           duration = float(ts_start) - float(ts_end)
       else:
           ts_end = ts_start + duration

      ts_start, ts_end = float(ts_start), float(ts_end)
      # Get the URL to the video page
      video_page_url = 'https://www.youtube.com/watch?v={}'.format(ytid)
      # filter out private and unavailable videos
      urls.append([video_page_url,[ts_start, duration]])
      print("\033[F"*3)
      print(f'YouTube ID: {ytid}', f'Trim Window: ({ts_start}, {ts_end})', sep='\n')
      print()
      print('--- Finding available videos: ---')
      av_urls = []
      with Pool(workers) as pool:
          for u in tqdm.tqdm(pool.imap_unordered(try_video, urls), total=len(urls)):
              av_urls.append(u)
              pass
     pool.terminate()
     pool.join()
     av_urls = [x for x in av_urls if x]
     print(f'Available urls: {len(av_urls)} / {len(urls)}')
     print()
     print('--- Finding best video and audio quality urls: ---')
     with Pool(workers) as pool:
         hq_urls = list(tqdm.tqdm(pool.imap_unordered(get_video_audio_urls, av_urls), total=len(av_urls)))
     pool.terminate()
     pool.join()
     hq_urls = [x for x in hq_urls if x]
     print(f'Downloadable/Public urls: {len(hq_urls)} / {len(urls)}')
     video_urls_for_download = []
     audio_urls_for_download = []
     for i,v in enumerate(hq_urls):
         yid = v[0].split('watch?v=')[-1]


         # Create path for videos
         if modality == 'video' or modality == 'audio-video':
             v_path = os.path.join(directory,'video',yid+'_'+str(int(v[1][0]))+'_'+str(int(v[1][0]+v[1][1]))+'.'+video_format)
             if not os.path.exists(os.path.join(directory,'video')):
                 os.makedirs(os.path.join(directory,'video'))

         if modality == 'audio' or modality == 'audio-video':
            a_path = os.path.join(directory,'audio',yid+'_'+str(int(v[1][0]))+'_'+str(int(v[1][0]+v[1][1]))+'.'+audio_container)
            if not os.path.exists(os.path.join(directory,'audio')):
                 os.makedirs(os.path.join(directory,'audio'))
         if modality == 'audio+video':
            a_path = os.path.join(directory,'video_with_audio',yid+'_'+str(int(v[1][0]))+'_'+str(int(v[1][0]+v[1][1]))+'.'+audio_container)
            if not os.path.exists(os.path.join(directory,'video_with_audio')):
                os.makedirs(os.path.join(directory,'video_with_audio'))

         if modality == 'video' or modality == 'audio-video':
             video_urls_for_download.append([ffmpeg_path,v[1][0],v[2][0],v[1][1],video_format,v_path])
         if modality == 'audio' or modality == 'audio-video':
             audio_urls_for_download.append([ffmpeg_path,v[1][0],v[2][1],v[1][1],audio_codec,a_path])
         if modality == 'audio+video':
             video_w_audio_urls_for_download.append([ffmpeg_path,v[1][0],v[2][2],v[1][1],video_format,v_path])


     print('--- Downloading video and audio w/ FFMPEG: ---')
     with Pool(workers) as pool:
        if modality == 'video' or modality == 'audio-video':
             for _ in tqdm.tqdm(pool.imap_unordered(video_downloader, video_urls_for_download), total=len(video_urls_for_download)):
                 pass
        if modality == 'audio' or modality == 'audio-video':
            for _ in tqdm.tqdm(pool.imap_unordered(audio_downloader, audio_urls_for_download), total=len(audio_urls_for_download)):
                pass
        if modality == 'audio+video':
            for _ in tqdm.tqdm(pool.imap_unordered(video_downloader, video_w_audio_urls_for_download), total=len(video_w_audio_urls_for_download)):
                pass
     pool.terminate()
     pool.join()
'''
---  E N D  O F  F U N C T I O N  D O W N L O A D ---
'''
