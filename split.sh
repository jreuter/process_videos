#! /bin/bash

FILE="$(ls *.mp4)"
echo $FILE
echo -en "\033]0;${FILE}\a"
FILE_LENGTH="$(ffmpeg -i "$FILE" 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,// | sed 's@\..*@@g' | awk '{ split($1, A, ":"); split(A[3], B, "."); print 3600*A[1] + 60*A[2] + B[1] }')"
EXPECTED_FPS=30

START=0
SIZE=120
SSIZE=30

mkdir pieces-${SIZE}sec
mkdir pieces-${SSIZE}sec
touch failures.txt

#touch fileList.txt
#echo "" > fileList.txt

# Split the video, check for flaws, etc.
while [[ $START -lt $FILE_LENGTH ]]; do
    ffmpeg -i "$FILE" -ss $START -t $SIZE -c copy -loglevel warning -stats pieces-${SIZE}sec/${START}.mp4
    # Check file for fps, if less than 30 (variable), create 30-sec clip.
    FPS="$(ffmpeg -i pieces-${SIZE}sec/${START}.mp4 2>&1 | sed -n "s/.*, \(.*\) fp.*/\1/p")"
    echo "FPS for video ${START} is ${FPS}."
    if [ $(echo "${FPS} < ${EXPECTED_FPS}" | bc) -ne 0 ]; then
        # add to failures list
        echo "${START}.mp4" >> failures.txt
        SSTART=${START}
        while [[ $SSTART -lt START+SIZE ]] && [[ $SSTART -lt $FILE_LENGTH  ]]; do
            ffmpeg -i "$FILE" -ss $SSTART -t $SSIZE -c:v libx264 -crf 20 -r ${EXPECTED_FPS} -force_key_frames "expr:gte(t,n_forced*1)" -loglevel warning -stats pieces-${SSIZE}sec/${SSTART}.mp4
            let SSTART=SSTART+SSIZE
        done
    fi
    #    echo "file pieces-${SIZE}sec/${START}.mp4" >> fileList.txt
    let START=START+SIZE
done

# If there are failures or if we know we want the first part split into 30sec sections.
if [ -s failures.txt ] || [ "$1" = "-f" ]; then
    START=0
    SIZE=120
    SSIZE=30
    # Split the first 2 minutes so any edits at the beginning don't jump to a strange keyframe.
    while [[ $START -lt $SIZE ]]; do
        ffmpeg -n -i "$FILE" -ss $START -t $SSIZE -c:v libx264 -crf 20 -r $EXPECTED_FPS -force_key_frames "expr:gte(t,n_forced*1)" -loglevel warning -stats pieces-${SSIZE}sec/${START}.mp4
        let START=START+SSIZE
    done
fi

mkdir all-files
mv -f pieces-${SIZE}sec/* all-files/
mv -f pieces-${SSIZE}sec/* all-files/

## Just combine the files. Only useful if I can get it to work with flowblade.
#ffmpeg -f concat -i fileList.txt -c copy ${FILE}-combined.mp4

rmdir pieces-${SIZE}sec
rmdir pieces-${SSIZE}sec

