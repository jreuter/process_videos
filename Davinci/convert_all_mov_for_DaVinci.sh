#!/bin/bash

if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg could not be found."
    exit
fi

echo "Checking Directory $1"

for i in "$1"/*.MOV; do
    [ -f "$i" ] || break

    echo "Processing File: $i"

    SCALE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$i" | tr , :)
    echo "Scale is $SCALE"

    ffmpeg -i "$i" -c:v dnxhd -vf "scale=$SCALE,fps=30000/1001,format=yuv422p" -b:v 90M -c:a pcm_s16le "$i.mxf"

done

