#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assemble the showcase video from static frames using snappy xfade
transitions (no zoompan/Ken Burns - avoids jitter, keeps full pages crisp
and readable), then mix in background music."""
import os
import subprocess

SCRIPTS = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site\scripts"
FR = os.path.join(SCRIPTS, "video_frames")
OUT_VIDEO = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site\assets\video\showcase.mp4"
OUT_POSTER = r"c:\Users\abrah\Desktop\Projects\דוגמאות לעלונים\site\assets\video\poster.jpg"
MUSIC = os.path.join(SCRIPTS, "audio", "happy_whistling_ukulele.mp3")

FPS = 30
T = 0.35  # transition duration (snappy)

# (scene name, hold duration incl. transition overlap, transition type INTO this scene)
scenes = [
    ("00_title", 2.6, None),
    ("01_vertical", 2.0, "circleopen"),
    ("02_horizontal", 2.0, "wipeleft"),
    ("03_styles", 2.3, "slideup"),
    ("04_sections", 2.3, "fade"),
    ("05_writers", 2.5, "wiperight"),
    ("06_family", 2.5, "circleclose"),
    ("07_sharing", 2.2, "slidedown"),
    ("08_bw", 2.3, "fade"),
    ("09_levels", 2.1, "wipeleft"),
    ("99_cta", 3.4, "slideright"),
]

durations = [s[1] for s in scenes]
names = [s[0] for s in scenes]
transitions = [s[2] for s in scenes[1:]]

inputs = []
for name, dur, _ in scenes:
    inputs += ["-loop", "1", "-t", f"{dur:.2f}", "-i", os.path.join(FR, f"{name}.png")]

filters = []
labels_in = [f"{i}:v" for i in range(len(scenes))]
cum = durations[0]
prev_label = labels_in[0]
for i in range(1, len(scenes)):
    trans = transitions[i - 1]
    offset = cum - T * i
    out_label = f"v{i}" if i < len(scenes) - 1 else "vout"
    filters.append(
        f"[{prev_label}][{labels_in[i]}]xfade=transition={trans}:duration={T}:offset={offset:.3f}[{out_label}]"
    )
    prev_label = out_label
    cum += durations[i]

total_dur = cum - T * (len(scenes) - 1)
filter_complex = ";".join(filters)

cmd = [
    "ffmpeg", "-y", *inputs,
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264",
    os.path.join(SCRIPTS, "video_clips", "silent_full.mp4"),
    "-loglevel", "error",
]
os.makedirs(os.path.join(SCRIPTS, "video_clips"), exist_ok=True)
print("Total (silent) duration ~", round(total_dur, 2))
print("Running ffmpeg xfade chain...")
subprocess.run(cmd, check=True)

# mix in music
silent = os.path.join(SCRIPTS, "video_clips", "silent_full.mp4")
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
     "default=noprint_wrappers=1:nokey=1", silent],
    capture_output=True, text=True, check=True,
)
video_dur = float(probe.stdout.strip())
fade_out_start = max(video_dur - 2.0, 0)

cmd2 = [
    "ffmpeg", "-y", "-i", silent, "-i", MUSIC,
    "-filter_complex",
    f"[1:a]atrim=0:{video_dur},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=2.0,volume=0.5[a]",
    "-map", "0:v", "-map", "[a]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
    OUT_VIDEO, "-loglevel", "error",
]
subprocess.run(cmd2, check=True)
print("Final video ->", OUT_VIDEO, "duration=", video_dur)

# poster
from PIL import Image
Image.open(os.path.join(FR, "04_sections.png")).save(OUT_POSTER, quality=88)
print("DONE")
