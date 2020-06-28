#! /bin/bash

#FILE="The Office - s02e17 - Dwight's Speech - V1221_20200525_122017.mp4"
FILE="$(ls *.mp4)"
echo $FILE
FILE_LENGTH="$(ffmpeg -i "$FILE" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }')"

START=0
SIZE=120

mkdir pieces-120sec
mkdir pieces-30sec

while [[ $START -lt $FILE_LENGTH ]]; do
    ffmpeg -i "$FILE" -ss $START -t $SIZE -c copy pieces-120sec/${START}.mp4
    let START=START+SIZE
done


START=0
SIZE=30
# If I can get the combine to work with flowblade, this would be helpful.
touch fileList.txt
echo "" > fileList.txt
while [[ $START -lt $FILE_LENGTH ]]; do
    ffmpeg -i "$FILE" -ss $START -t $SIZE -c copy pieces-30sec/${START}.mp4
    # Split, re-encode with keyframes every 1 second, 30 fps and quality 20.
    ffmpeg -i "$FILE" -ss $START -t $SIZE -c:v libx264 -crf 20 -r 30 -force_key_frames "expr:gte(t,n_forced*1)" pieces-30sec/${START}.mp4
    echo "file pieces-30sec/${START}.mp4" >> fileList.txt
    let START=START+SIZE
done

## Just combine the files. Only useful if I can get it to work with flowblade.
#ffmpeg -f concat -i fileList.txt -c copy combined.mp4

