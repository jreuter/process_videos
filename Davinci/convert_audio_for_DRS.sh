#!/bin/bash

if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg could not be found."
    exit
fi

echo "Checking Directory $1"

# Enable case-insensitive globbing
shopt -s nocaseglob
# Enable nullglob to prevent the loop from running with the literal pattern if no files match
shopt -s nullglob

#find "$1" -iname \*.MP4 -o -iname \*.mp4 | while read f; do
for i in "$1"/*.MP4; do
    [ -f "$i" ] || break

    echo "Processing File: $i"

    SCALE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$i" | tr , :)
    echo "Scale is $SCALE"

    # MP4 files 23.97
#    ffmpeg -i "$i" -c:v dnxhd -vf "scale=$SCALE,fps=24000/1001,format=yuv422p" -b:v 90M -c:a pcm_s16le "$i.mxf"

    # MP$ Files 29.97
#    ffmpeg -i "$i" -c:v dnxhd -vf "scale=$SCALE,fps=30000/1001,format=yuv422p" -b:v 90M -c:a pcm_s16le "$i.mxf"

    ffmpeg -i "$i" -acodec pcm_s16le -vcodec copy "$i-pcm.mov"

done

# Optional: Disable nocaseglob to restore default behavior
shopt -u nocaseglob


#ffmpeg -i "FBB13501.mkv" -map 0 -c copy -c:a aac "FBB13501-1080p.MP4"

#ffmpeg -i DY5A1751.MP4 -acodec pcm_s16le -vcodec copy DY5A1751-pcm.mov


