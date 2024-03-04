#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

"""
Program to organize video recordings into directories and convert them for use in DaVinci Resolve.

This was created to handle video files from my cameras.  This takes Camera A footage from my camera connected to OBS
on my laptop (an MKV output) and Camera B footage which is a bunch of ~30 minute clips from my Canon t5i.  It also
handles audio files from my DJI mics.  This also will extract audio from the Camera A footage as that can be used
for the 'quick edit' for people who missed the class.

Usage:
    process_recordings [options] <folder>
    process_recordings -h | --help
    process_recordings --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -q              Quiet the logging to only ERROR level.
    -v              Verbose output (INFO level).
    --quick         Quick edit files only.
    --debug         Very Verbose output (DEBUG level).
"""
import os, sys, re
from docopt import docopt
from shutil import copy2
import ffmpeg
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s %(levelname)s %(message)s')

class ProcessRecordings:
    _arguments = None
    _log_level = 'WARN'
    _folder = ''

    def __init__(self):
        """
        Gets command line arguments using docopt and sets logging level.
        """
        self._arguments = docopt(__doc__, version='0.1')
        self._set_logging_verbosity()

    def _set_logging_verbosity(self):
        """
        Sets the logging level based on arguments passed in the cli.
        """
        if self._arguments['-v']:
            self._log_level = logging.INFO
        if self._arguments['--debug']:
            self._log_level = logging.DEBUG
        if self._arguments['-q']:
            self._log_level = logging.ERROR
        logging.basicConfig(level=self._log_level,
                            format='%(asctime)s %(message)s')

    def main(self):
        directories = {
            "source": "Original Source",
            "dest": "Resolve Imports"
        }
        existing_dirs = []
        files = []
        movs = []
        mkvs = []
        mkv_regex = "(.*).mkv$"
        mov_regex = "(.*).MOV$"

        logging.info('Directory added: %s', self._arguments['<folder>'])
        self._folder = self._arguments['<folder>']

        # Make sure it's a folder before processing.
        if os.path.isfile(self._folder):
            logging.error('Program only handles folders.')
            exit(1)

        # Make sure it's not a dot folder (may be removed later).
        if os.path.basename(self._folder).startswith('.'):
            logging.error('Ignoring dot folders.')
            exit()

        # Get all files in directory.
        for (dirpath, dirnames, filenames) in os.walk(self._folder):
            existing_dirs.extend(dirnames)
            files.extend(filenames)
            break
        for file in files:
            tmp = re.findall(mov_regex, file)
            if len(tmp) > 0:
                logging.info("Adding file {} to list for processing.".format(file))
                movs.append(tmp[0])
        for file in files:
            tmp = re.findall(mkv_regex, file)
            if len(tmp) > 0:
                logging.info("Adding file {} to list for processing.".format(file))
                mkvs.append(tmp[0])

        # Make directories and move files.
        for value in directories.values():
            directory = os.path.join(self._folder, value)
            if not os.path.exists(directory):
                logging.info("Creating directory {}.".format(directory))
                os.makedirs(directory)

        for x in dirnames:
            print(f'Moving directory {x} to {directories["source"]}')
            os.rename(os.path.join(self._folder, x), os.path.join(self._folder, directories['source'], x))

        for x in movs:
            tmp_filename = x + ".MOV"
            logging.debug("Moving " + tmp_filename + " from " + os.path.join(self._folder, tmp_filename) +
                          "\n to " + os.path.join(self._folder, directories['source'], tmp_filename))
            print(("Processing file {}".format(tmp_filename)))
            os.rename(os.path.join(self._folder, tmp_filename), os.path.join(self._folder, directories['source'], tmp_filename))

        for x in mkvs:
            tmp_filename = x + ".mkv"
            logging.debug("Moving " + tmp_filename + " from " + os.path.join(self._folder, tmp_filename) +
                          "\n to " + os.path.join(self._folder, directories['source'], tmp_filename))
            print(("Processing file {}".format(tmp_filename)))
            os.rename(os.path.join(self._folder, tmp_filename),
                      os.path.join(self._folder, directories['source'], tmp_filename))

        # Extact Audio Wav for Quick Edit
        for x in mkvs:
            source_file = x + '.mkv'
            source_path = os.path.join(self._folder, directories['source'], source_file)
            dest_file = x + '-audio.wav'
            dest_path = os.path.join(self._folder, directories['dest'], dest_file)
            print(f'Dest path is {dest_path}')
            # ffmpeg.input(source_path).output(dest_path,
            #                                  '-vn',
            #                                  **{'acodec': 'pcm_s16le'},
            #                                  **{'ar': 44100},
            #                                  **{'ac': 2})

        # Process MOV Videos
        for x in movs:
            filename = x + '.MOV'
            file_path = os.path.join(self._folder, directories['source'], filename)
            dest_file = x + '.mxf'
            dest_path = os.path.join(self._folder, directories['dest'], dest_file)
            ffprobe = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', file_path]
            translate = ['tr', ',', ':']
            ffprobe_proc = subprocess.Popen(ffprobe, stdout=subprocess.PIPE, text=True)
            translate_proc = subprocess.Popen(translate, stdin=ffprobe_proc.stdout, stdout=subprocess.PIPE, text=True)
            scale, error = translate_proc.communicate()
            # Build Video Format based on ffprobe data.
            # TODO: Add fps here as well.
            video_format = f'scale={scale},fps=30000/1001,format=yuv422p'
            ffmpeg.input(file_path).output(dest_path,
                                           **{'c:v': 'dnxhd'},
                                           **{'c:a': 'pcm_s16le'},
                                           **{'vf': video_format},
                                           **{'b:v': '90M'},
                                           loglevel="quiet").run()

if __name__ == '__main__':
    ProcessRecordings().main()