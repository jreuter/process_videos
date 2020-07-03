#!/usr/bin/env python2.7
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
import os, sys, re
from docopt import docopt
from shutil import copy2
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s %(levelname)s %(message)s')


class ProcessVideos:
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
            logging.error('Ignoring dot folders.')
            exit()

        # Get all files in directory.
        for (dirpath, dirnames, filenames) in os.walk(self._folder):
            files.extend(filenames)
            break
        for file in files:
            tmp = re.findall(mp4_regex, file)
            if len(tmp) > 0:
                logging.info("Adding file {} to list for processing.".format(file))
                directories.append(tmp[0])

        # Get all files in the directory, but only files.
        # files = [os.path.splitext(f)[0] for f in os.listdir(self._folder)
        #          if os.path.isfile(os.path.join(self._folder, f))]

        logging.debug(directories)

        for x in directories:
            directory = os.path.join(self._folder, x)
            if not os.path.exists(directory):
                logging.info("Creating directory {}.".format(directory))
                os.makedirs(directory)
            tmp_filename = x + ".mp4"
            logging.debug("Moving " + tmp_filename + " from " + os.path.join(self._folder, tmp_filename) +
                          "\n to " + os.path.join(self._folder, x, tmp_filename))
            print("Processing file {}".format(tmp_filename))
            os.rename(os.path.join(self._folder, tmp_filename), os.path.join(self._folder, x, tmp_filename))
            copy2(os.path.join("./", "split.sh"), os.path.join(self._folder, x))

        if self._arguments['-s']:
            for i, name in enumerate(directories, start=1):
                directory = os.path.join(self._folder, name)
                print("\n\nProcessing {} of {}: {}\n\n".format(i, len(directories), name))
                os.chdir(directory)
                process = subprocess.Popen("./split.sh", shell=True, stdout=subprocess.PIPE)
                process.wait()


if __name__ == '__main__':
    ProcessVideos().main()
