#!/bin/bash

if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg could not be found."
    exit
fi

echo "$1"

SCALE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$1" | tr , :)

echo $SCALE

FPS=$(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "$1")

echo $FPS


#FORMAT=$(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_format $1)

#FORMAT=$(ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries format $1)
#echo $FORMAT

BITRATE=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$1")
echo $BITRATE

# Example: ffmpeg -i input -c:v dnxhd -vf "scale=1280:720,fps=30000/1001,format=yuv422p" -b:v 110M -c:a pcm_s16le output.mov

## This was used for phone videos.  'dnxhd' is h264
#ffmpeg -i "$1" -c:v dnxhd -vf "scale=$SCALE,fps=$FPS,format=yuv422p" -b:v 115M -c:a pcm_s16le "$1".MOV

## This is my attempt for TV Recordings, which are currently MPEG-4
#ffmpeg -i "$1" -c:v mpeg4 -vf "scale=$SCALE,fps=2397/100,format=yuv422p" -b:v $BITRATE -c:a pcm_s16le "$1.MOV"

## This is for mkv files from OBS.
ffmpeg -i "$1" -c:v dnxhd -vf "scale=$SCALE,fps=30000/1001,format=yuv422p" -b:v 90M -c:a pcm_s16le "$1.mxf"

## All MOV Files from Canon T5i

