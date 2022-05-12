from macrawlon import download


print('Test 1 for 1K video-only files:')


download(
  csv_dir='examples/vggsound_1K.csv',
  download_dir='data/vggsound_video_only',
  modality='video',
  resolutions=[480, 360],
  id_idx = 0,
  start_idx = 1,
  duration = 10,
  workers=5
  )
