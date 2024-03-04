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
import ffmpeg
import logging
import subprocess
from tqdm import tqdm

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s %(levelname)s %(message)s')

class ProcessRecordings:
    _arguments = None
    _log_level = 'WARN'
    _folder = ''
    _directories = {
        "source": "Original Source",
        "dest": "Resolve Imports"
    }

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

    def move_to_source(self, file, ext):
        tmp_filename = file + f'.{ext}'
        logging.debug("Moving " + tmp_filename + " from " + os.path.join(self._folder, tmp_filename) +
                      "\n to " + os.path.join(self._folder, self._directories['source'], tmp_filename))
        print(f'Moving file {tmp_filename} to {self._directories["source"]}')
        os.rename(os.path.join(self._folder, tmp_filename),
                  os.path.join(self._folder, self._directories['source'], tmp_filename))

    def convert_to_mxf(self, file, ext):
        filename = file + f'.{ext}'
        file_path = os.path.join(self._folder, self._directories['source'], filename)
        dest_file = file + '.mxf'
        dest_path = os.path.join(self._folder, self._directories['dest'], dest_file)
        ffprobe = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of',
                   'csv=p=0', file_path]
        translate = ['tr', ',', ':']
        ffprobe_proc = subprocess.Popen(ffprobe, stdout=subprocess.PIPE, text=True)
        translate_proc = subprocess.Popen(translate, stdin=ffprobe_proc.stdout, stdout=subprocess.PIPE, text=True)
        scale, error = translate_proc.communicate()
        # Build Video Format based on ffprobe data.
        # TODO: Add fps here as well.
        video_format = f'scale={scale},fps=30000/1001,format=yuv422p'
        probe = ffmpeg.probe(file_path)
        print(f'Frames is {probe["streams"][0]["nb_frames"]}')
        print(f'Total duration is {probe["streams"][0]["duration"]}')
        # total_duration = probe["streams"][0]["duration"]
        ffmpeg.input(file_path).output(dest_path,
                                       **{'c:v': 'dnxhd'},
                                       **{'c:a': 'pcm_s16le'},
                                       **{'vf': video_format},
                                       **{'b:v': '90M'},
                                       loglevel="quiet").run()
                                       # **{'progress': '-'}).run()

        ## Beginning of solution I found here: https://github.com/kkroening/ffmpeg-python/blob/master/examples/show_progress.py
        ## This might require too many changes though.
        ## Here is another similar solution: https://gist.github.com/pbouill/fddf767221b47f83c97d7813c03569c4
        ## More resources: https://stackoverflow.com/questions/7632589/getting-realtime-output-from-ffmpeg-to-be-used-in-progress-bar-pyqt4-stdout
        ## https://github.com/althonos/ffpb
        # with show_progress(total_duration) as socket_filename:
        #     (ffmpeg.input(file_path).output(dest_path,
        #                                    **{'c:v': 'dnxhd'},
        #                                    **{'c:a': 'pcm_s16le'},
        #                                    **{'vf': video_format},
        #                                    **{'b:v': '90M'},
        #                                    loglevel="quiet")
        #                             .global_args('-progress', 'unix://{}'.format(socket_filename)))

        ## Example progress output
        # frame = 379
        # fps = 53.98
        # stream_0_0_q = 4.0
        # bitrate = 41754.4kbits / s
        # total_size = 73143316
        # out_time_us = 14014000
        # out_time_ms = 14014000
        # out_time = 00:00:14.014000
        # dup_frames = 0
        # drop_frames = 0
        # speed = 2x
        # progress = continue

    def main(self):
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
        print('Searching for MOV files.')
        for file in files:
            tmp = re.findall(mov_regex, file)
            if len(tmp) > 0:
                logging.info("Queueing file {} to list for processing.".format(file))
                movs.append(tmp[0])
        print('Searching for MKV files.')
        for file in files:
            tmp = re.findall(mkv_regex, file)
            if len(tmp) > 0:
                logging.info("Queueing file {} to list for processing.".format(file))
                mkvs.append(tmp[0])

        # Make directories and move files.
        print('Creating Folder Structure.')
        for value in self._directories.values():
            directory = os.path.join(self._folder, value)
            if not os.path.exists(directory):
                logging.info("Creating directory {}.".format(directory))
                os.makedirs(directory)

        print('Looking for other source folders.')
        for x in existing_dirs:
            print(f'Moving directory {x} to {self._directories["source"]}')
            os.rename(os.path.join(self._folder, x), os.path.join(self._folder, self._directories['source'], x))

        for x in movs:
            self.move_to_source(x, 'MOV')

        for x in mkvs:
            self.move_to_source(x, 'mkv')

        # Extact Audio Wav for Quick Edit
        for x in mkvs:
            source_file = x + '.mkv'
            source_path = os.path.join(self._folder, self._directories['source'], source_file)
            dest_file = x + '-audio.wav'
            dest_path = os.path.join(self._folder, self._directories['dest'], dest_file)
            print(f'Extracting Camera A Audio to {dest_path}')
            stream_input = ffmpeg.input(source_path)
            ffmpeg.output(stream_input.audio, dest_path,
                          **{'acodec': 'pcm_s16le'},
                          **{'ar': 44100},
                          **{'ac': 2},
                          loglevel="quiet").run()

        # Process MOV Videos
        print('Processing MOV Files from Camera B.')
        for x in movs:
            self.convert_to_mxf(x, "MOV")

        # Process Camera A Footage
        print('Processing MKV Files from Camera A.')
        for x in mkvs:
            self.convert_to_mxf(x, 'mkv')


if __name__ == '__main__':
    ProcessRecordings().main()
