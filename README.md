# process_videos

Does some pre-processing of TV recordings before editing.

## Why?

I originally came up with this code because I had an HDMI recorder to record live TV to USB.  This device was 
occasionally producing files that were corrupt.  They would play find, but if I wanted to edit the files to trim the 
beginning and end or remove commercials the results would have audio/video sync issues.

### The "Fix"

I came up with the concept of splitting the files and checking for where the dropped frames existed in the recording.  
This is the file `split.sh` which uses `ffmpeg` to split each file into 2-minute chunks and check each for their 
FPS.  If there is a failure in any 2-minute chunk, it further splits that piece into 30-second chunks.  If this is a 
live program and re-recording is not an option, I can put all these back together in an editor and the audio/video 
sync issue will only exist in that 30-second chunk.  This gives a watchable file even if there are a couple seconds 
with a glitch.

### Batch processing

There were moments where I had many recording, perhaps a season of a show.  I created some python code to make batch 
processing all these videos a little easier.  The `process_videos.py` script takes a directory as input and will 
make folders for each episode in that directory, and copy the `split.sh` file to each for later processing.  I later 
added the `-s` option to queue and split the files for me (execute the `split.sh` for each).  This will also output 
a list of the damaged files in the terminal so you don't need to check in each folder to see how they did.

### Cleanup

I created the `post_process.py` script to help put this expanded directory structure into something sane for me.  
By default is removes all the folders and chunks created before, but keeps the original file.  If you use the `-f` 
option, it will move those files back to their parent directory and remove the folder for each episode.  By default, 
the deleted files will be moved to the trash instead of deleted so you can recover if you need.  Passing in the `-p` 
flag makes these permanent deletes instead.

### Requirements

The default option for `post_process` is to send files/folders to the trash instead of a permanent deleted.  
This requires a 3rd party app `send2trash`.

Install Requirements.

```bash
       python -m pip install --user send2trash
```

For Python3:

```bash
        python3 -m pip install --user send2trash
```

