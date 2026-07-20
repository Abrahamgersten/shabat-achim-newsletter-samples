#!/bin/bash
set -e
cd "$(dirname "$0")"
FR="video_frames"
CL="video_clips"
mkdir -p "$CL"

# name:duration:motion
# motion: zoomin | zoomout | panlr | panrl | subtle
scenes=(
  "00_title:4.2:subtle"
  "01_vertical:4.0:zoomin"
  "02_horizontal:4.0:panlr"
  "03_styles:3.8:zoomout"
  "04_sections:4.0:zoomin"
  "05_sharing:3.6:panrl"
  "06_bw:4.0:zoomin"
  "07_levels:3.8:panlr"
  "08_activity1:3.6:zoomout"
  "09_activity2:3.6:panrl"
  "99_cta:4.8:subtle"
)

FPS=30

zoompan_expr() {
  local motion="$1" frames="$2"
  case "$motion" in
    zoomin)
      echo "z='min(zoom+0.0010,1.11)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=$FPS"
      ;;
    zoomout)
      echo "z='if(eq(on,0),1.11,max(zoom-0.0010,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=$FPS"
      ;;
    panlr)
      echo "z='1.14':x='(iw-iw/zoom)*(on/($frames-1))':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=$FPS"
      ;;
    panrl)
      echo "z='1.14':x='(iw-iw/zoom)*(1-on/($frames-1))':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=$FPS"
      ;;
    subtle)
      echo "z='min(zoom+0.0004,1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=$FPS"
      ;;
  esac
}

for entry in "${scenes[@]}"; do
  name="${entry%%:*}"
  rest="${entry#*:}"
  dur="${rest%%:*}"
  motion="${rest##*:}"
  frames=$(python -c "print(round($dur*$FPS))")
  fade_dur=0.4
  expr=$(zoompan_expr "$motion" "$frames")
  echo "encoding $name dur=$dur motion=$motion frames=$frames"
  ffmpeg -y -loop 1 -i "$FR/$name.png" \
    -vf "zoompan=$expr,fade=t=in:st=0:d=$fade_dur,fade=t=out:st=$(python -c "print($dur-$fade_dur)"):d=$fade_dur" \
    -t "$dur" -c:v libx264 -pix_fmt yuv420p -r $FPS -an "$CL/$name.mp4" -loglevel error
done

# concat (silent)
listfile="$CL/list.txt"
> "$listfile"
total_dur=0
for entry in "${scenes[@]}"; do
  name="${entry%%:*}"
  rest="${entry#*:}"
  dur="${rest%%:*}"
  echo "file '$name.mp4'" >> "$listfile"
  total_dur=$(python -c "print($total_dur + $dur)")
done

ffmpeg -y -f concat -safe 0 -i "$listfile" -c copy "$CL/silent_full.mp4" -loglevel error
echo "Silent video assembled, duration≈$total_dur"

# mix in music: trim to video length, fade in/out, moderate volume
music="audio/happy_whistling_ukulele.mp3"
video_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$CL/silent_full.mp4")
fade_out_start=$(python -c "print(max($video_dur-2.2,0))")

ffmpeg -y -i "$CL/silent_full.mp4" -i "$music" \
  -filter_complex "[1:a]atrim=0:$video_dur,afade=t=in:st=0:d=1.5,afade=t=out:st=$fade_out_start:d=2.2,volume=0.5[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 160k -shortest \
  "../assets/video/showcase.mp4" -loglevel error

echo "Final video with music -> ../assets/video/showcase.mp4"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "../assets/video/showcase.mp4"

# poster frame from a contain-fit newsletter scene
python -c "
from PIL import Image
im = Image.open('$FR/04_sections.png')
im.save('../assets/video/poster.jpg', quality=88)
"
echo "DONE"
