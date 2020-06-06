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
    ffmpeg -i "$FILE" -force_key_frames "expr:gtr(t,n_forced*3)" -ss $START -t $SIZE -c copy pieces-120sec/${START}.mp4
    let START=START+SIZE
done


START=0
SIZE=30
while [[ $START -lt $FILE_LENGTH ]]; do
    ffmpeg -i "$FILE" -force_key_frames "expr:gtr(t,n_forced*3)" -ss $START -t $SIZE -c copy pieces-30sec/${START}.mp4
    let START=START+SIZE
done
