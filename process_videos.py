#!/usr/bin/python -O
# -*- coding: utf-8 -*-

"""
Program to organize video recordings into directories and split them into small clips.

Usage:
    process_videos [options] <folder>
    process_videos -h | --help
    process_videos --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -q              Quiet the logging to only ERROR level.
    -v              Verbose output (INFO level).
    -s              Queue up and Split videos.
    --debug         Very Verbose output (DEBUG level).
"""
import os, sys, array, unittest, random, re
from docopt import docopt
from shutil import copy2
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s %(levelname)s %(message)s')


class ProcessVideos:
    _arguments = None
    _log_level = 'WARN'
    _default_size = 1920, 1080
    _folder = ''
    _thread_list = []

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
        files = []
        directories = []
        fileStructure = {}
        mp4_regex = "(.*).mp4$"
        # full_path = os.path.join(self._folder, image)

        logging.info('Directory added: %s', self._arguments['<folder>'])
        self._folder = self._arguments['<folder>']

        # Make sure it's a folder before processing.
        if os.path.isfile(self._folder):
            logging.error('Program only handles folders.')
            exit(1)

        # Make sure it's not a dot folder (may be removed later).
        if os.path.basename(self._folder).startswith('.'):
            logging.info('Ignoring dot folders.')
            exit()

        # Get all files in directory.
        for (dirpath, dirnames, filenames) in os.walk(self._folder):
            files.extend(filenames)
            break
        for file in files:
            print("checking file : " + file)
            tmp = re.findall(mp4_regex, file)
            if len(tmp) > 0:
                directories.append(tmp[0])

        # Get all files in the directory, but only files.
        # files = [os.path.splitext(f)[0] for f in os.listdir(self._folder)
        #          if os.path.isfile(os.path.join(self._folder, f))]

        print(directories)

        for x in directories:
            directory = os.path.join(self._folder, x)
            if not os.path.exists(directory):
                os.makedirs(directory)
            tmp_filename = x + ".mp4"
            print("Moving " + tmp_filename + " from " + os.path.join(self._folder, tmp_filename) + " to " + os.path.join(self._folder, x, tmp_filename))
            os.rename(os.path.join(self._folder, tmp_filename), os.path.join(self._folder, x, tmp_filename))
            copy2(os.path.join("./", "split.sh"), os.path.join(self._folder, x))


if __name__ == '__main__':
    ProcessVideos().main()
