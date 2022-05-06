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

res_options = ['480', '360' ,'240']

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

def try_video(url):
    v_url = url[0]
    pattern = '"playabilityStatus":{"status":"ERROR"'
    request = requests.get(v_url)
    is_True= False if pattern in request.text else True
    if not is_True:
        return ""
    return url

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
        best_video_url = best_video.url
        best_audio = video.getbestaudio()
        best_audio_url = best_audio.url
        return (url[0], url[1], [best_video_url, best_audio_url])
    except Exception as e:
        print(e)
        return


    return


# Set output settings
audio_codec = 'flac'
audio_container = 'flac'
video_codec = 'h264'
video_format = 'mp4'
directory='VGGsound'
id_idx = 0
start_idx = 1
end_idx = None
duration=10

# Load the AudioSet training set
df = pd.read_csv('VGGSound/data/vggsound_10K.csv')
urls = []
times = []

print("\n"*3, end="")
# Iterate over videos
for index, row in df.iterrows():
    if index>1000:
        break
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
    print(f'YouTube ID: {ytid}',
          f'Trim Window: ({ts_start}, {ts_end})',
          sep='\n')
print()
print('--- Finding available videos: ---')
av_urls = []
with Pool() as pool:
    for u in tqdm.tqdm(pool.imap_unordered(try_video, urls), total=len(urls)):
        av_urls.append(u)
        pass
pool.terminate()
pool.join()
av_urls = [x for x in av_urls if x]
print(f'Available urls: {len(av_urls)} / {len(urls)}')
print()
print('--- Finding best video and audio quality urls: ---')
with Pool() as pool:
    hq_urls = list(tqdm.tqdm(pool.imap_unordered(get_video_audio_urls, av_urls), total=len(av_urls)))
pool.terminate()
pool.join()
hq_urls = [x for x in hq_urls if x]
print(f'Downloadable/Public urls: {len(hq_urls)} / {len(urls)}')
video_urls_for_download = []
audio_urls_for_download = []
for i,v in enumerate(hq_urls):

    yid = v[0].split('watch?v=')[-1]
    v_path = os.path.join(directory,'video',yid+'_'+str(int(v[1][0]))+'_'+str(int(v[1][0]+v[1][1]))+'.'+video_format)
    if not os.path.exists(os.path.join(directory,'video')):
        os.makedirs(os.path.join(directory,'video'))

    a_path = os.path.join(directory,'audio',yid+'_'+str(int(v[1][0]))+'_'+str(int(v[1][0]+v[1][1]))+'.'+audio_container)
    if not os.path.exists(os.path.join(directory,'audio')):
        os.makedirs(os.path.join(directory,'audio'))

    video_urls_for_download.append([ffmpeg_path,v[1][0],v[2][0],v[1][1],video_format,v_path])
    audio_urls_for_download.append([ffmpeg_path,v[1][0],v[2][1],v[1][1],audio_codec,a_path])

print('--- Downloading video and audio w/ FFMPEG: ---')
with Pool() as pool:
    for _ in tqdm.tqdm(pool.imap_unordered(video_downloader, video_urls_for_download), total=len(video_urls_for_download)):
        pass
    for _ in tqdm.tqdm(pool.imap_unordered(audio_downloader, audio_urls_for_download), total=len(audio_urls_for_download)):
        pass
pool.terminate()
pool.join()
