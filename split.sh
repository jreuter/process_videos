#! /bin/bash

FILE="$(ls *.mp4)"
echo $FILE
FILE_LENGTH="$(ffmpeg -i "$FILE" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }')"

START=0
SIZE=120

mkdir pieces-120sec
mkdir pieces-30sec
touch failures.txt

#touch fileList.txt
#echo "" > fileList.txt

while [[ $START -lt $FILE_LENGTH ]]; do
    ffmpeg -i "$FILE" -ss $START -t $SIZE -c copy pieces-120sec/${START}.mp4
    # Check file for fps, if less than 30 (variable), create 30-sec clip.
    FPS="$(ffmpeg -i pieces-120sec/${START}.mp4 2>&1 | sed -n "s/.*, \(.*\) fp.*/\1/p")"
    echo "FPS for video ${START} is ${FPS}."
    if [ $(echo "${FPS} < 30" | bc) -ne 0 ]; then
        # add to failures list
        echo "pieces-120sec/${START}.mp4" >> failures.txt
        SSTART=${START}
        SSIZE=30
        while [[ $SSTART -lt START+SIZE ]] && [[ $SSTART -lt $FILE_LENGTH  ]]; do
            ffmpeg -i "$FILE" -ss $SSTART -t $SSIZE -c:v libx264 -crf 20 -r 30 -force_key_frames "expr:gte(t,n_forced*1)" pieces-30sec/${SSTART}.mp4
            let SSTART=SSTART+SSIZE
        done
    fi
#    echo "file pieces-120sec/${START}.mp4" >> fileList.txt
    let START=START+SIZE
done

mkdir all-files
mv -f pieces-120sec/* all-files/
mv -f pieces-30sec/* all-files/

## Just combine the files. Only useful if I can get it to work with flowblade.
#ffmpeg -f concat -i fileList.txt -c copy ${FILE}-combined.mp4

rmdir pieces-120sec
rmdir pieces-30sec

