#!/bin/bash
set -e
cd "$(dirname "$0")"
FR="video_frames"
CL="video_clips"
mkdir -p "$CL"

# name:duration (seconds)
scenes=(
  "00_title:4.2"
  "01_vertical:3.4"
  "02_horizontal:3.4"
  "03_styles:3.6"
  "04_sections:3.6"
  "05_sharing:3.6"
  "06_bw:3.6"
  "07_levels:3.4"
  "08_activity1:3.6"
  "09_activity2:3.6"
  "99_cta:4.8"
)

FPS=30

for entry in "${scenes[@]}"; do
  name="${entry%%:*}"
  dur="${entry##*:}"
  frames=$(python -c "print(round($dur*$FPS))")
  fade_dur=0.4
  echo "encoding $name dur=$dur frames=$frames"
  ffmpeg -y -loop 1 -i "$FR/$name.png" \
    -vf "zoompan=z='min(zoom+0.0009,1.09)':d=$frames:s=1280x720:fps=$FPS,fade=t=in:st=0:d=$fade_dur,fade=t=out:st=$(python -c "print($dur-$fade_dur)"):d=$fade_dur" \
    -t "$dur" -c:v libx264 -pix_fmt yuv420p -r $FPS -an "$CL/$name.mp4" -loglevel error
done

# concat
listfile="$CL/list.txt"
> "$listfile"
for entry in "${scenes[@]}"; do
  name="${entry%%:*}"
  echo "file '$name.mp4'" >> "$listfile"
done

ffmpeg -y -f concat -safe 0 -i "$listfile" -c copy "../assets/video/showcase.mp4" -loglevel error

echo "Video assembled -> ../assets/video/showcase.mp4"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "../assets/video/showcase.mp4"

# poster frame from title card
python -c "
from PIL import Image
im = Image.open('$FR/04_sections.png')
im.save('../assets/video/poster.jpg', quality=85)
"
echo "DONE"
