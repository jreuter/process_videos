#!/usr/bin/env python2.7
#  -*- coding: utf-8 -*-

"""
Remove the 'all-files' directory generated for each split script on a batch of videos.

Usage:
    post_process    [options] <folder>
    post_process    -h | --help
    post_process    --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -q              Quiet the logging to only ERROR level.
    -v              Verbose output (INFO level).
    -p              Permanently remove files/folders.  Default is move to trash.
    --debug         Very Verbose output (DEBUG level).
"""
import os, sys
from docopt import docopt
from send2trash import send2trash
import shutil
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(asctime)s %(levelname)s %(message)s')


class PostProcess:
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
        directories = []

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
            directories.extend(dirnames)
            break
        print(directories)
        for x in directories:
            directory = os.path.join(self._folder, x, 'all-files')
            if os.path.exists(directory):
                print("We would remove {}".format(directory))
                if self._arguments['-p']:
                    # Permanently delete the files without prompting the user.
                    shutil.rmtree(directory, ignore_errors=True)
                else:
                    # https://stackoverflow.com/a/4773369
                    send2trash(directory)


if __name__ == '__main__':
    PostProcess().main()
