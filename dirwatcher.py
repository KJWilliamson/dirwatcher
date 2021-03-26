#!/usr/bin/env python3
"""
Dirwatcher - A long running program
that watches a chosen directory and searches
 the text for a "magic" string.
- And then logs it when the "magic" string is found.
This handles exceptions to allow program to continue running
"""

__author__ = "kamela williamson"
# for create_parser looked at tdd assessment
# looked at all previous assessments
# Daniel's workshop demos for assessment & sprint
# read README a bazillion times. lol
# used hints from README & sprint & workshop code
# https://realpython.com/python-logging/
# https://docs.python.org/3/library/logging.html
# https://docs.python.org/3/tutorial/errors.html
# https://realpython.com/python-exceptions/
# https://www.youtube.com/watch?v=NIWwJbo-9_8&feature=emb_logo
# https://pymotw.com/3/signal/
# https://www.stackabuse.com/handling-unix-signals-in-python/
# https://linoxide.com/linux-how-to/linux-signals-part-1/
# https://docs.python.org/3/library/signal.html
# https://www.askpython.com/python-modules/python-signal
# https://www.youtube.com/watch?v=_r4BhyEcWeY
# https://www.youtube.com/watch?v=Zvd2NuwKtS8&amp%3Bt=2s
# https://docs.python.org/3/library/os.path.html
# https://www.tutorialspoint.com/python/os_listdir.htm
# https://www.w3schools.com/python/python_variables_global.asp
# https://www.w3schools.com/python/ref_string_endswith.asp
# https://www.w3schools.com/python/ref_list_remove.asp
# https://docs.python.org/3/library/errno.html
# http://introtopython.org/dictionaries.html
# https://www.geeksforgeeks.org/logging-in-python/
# https://flaviocopes.com/python-command-line-arguments/

# hints! break up your code into small functions
# scan_single_file()
# detect_added_files()
# detect_removed_files()
# watch_directory()

import sys
import argparse
import time
import logging
import signal
import os
import errno

# global
exit_flag = False
watch_files = {}
# # Create a custom logger
logger = logging.getLogger(__name__)


def search_for_magic(filename, start_line, magic_string):
    """ Looks in files for magic string """
    # Your code here
    l_num = 0
    with open(filename) as f:
        for l_num, line in enumerate(f):
            if l_num >= start_line:
                if magic_string in line:
                    logger.info(
                        f'File found: {magic_string} '
                        f'Found on line: {l_num+1} in {filename}'
                    )

    return l_num + 1


def watch_directory(path, magic_string, extension, interval):
    """ Monitors the directory """
    # Your code here
    f_list = os.listdir(path)
    detect_added_files(f_list, extension)
    detect_removed_files(f_list)
    for f in watch_files:
        f_list = os.l_path.join(path, f)
        watch_files[f] = search_for_magic(
            path,
            watch_files[f],
            magic_string
        )
    return watch_files


def create_parser():
    """ Argparse helper. Creates parser and setup command line options """
    # Your code here
    # path & magic are required for program to run
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string")
    parser.add_argument("path", help="directory path to watch")
    parser.add_argument("magic_string", help="string to watch for")
    parser.add_argument("-e", "--extension", default=".txt",
                        help="extension to watch")
    parser.add_argument("-i", "--interval", default=1, help="sets interval")

    return parser


def detect_added_files(f_list, ext):
    # checks if new file added
    # need files added with magic text
    global watch_files
    for f in f_list:
        if f.endswith(ext) and f not in watch_files:
            watch_files[f] = 0
            logger.info(
                f'Magic text found in file, '
                f'{f} added to watch dir'
                )
    return f_list


def detect_removed_files(f_list):
    # checks for deleted files
    global watch_files
    for f in list(watch_files):
        if f not in f_list:
            logger.info(f'{f} removed from watch dir')
            del watch_files[f]
    return f_list


def signal_handler(sig_num, frame):
    """ This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
     as well (SIGHUP?) Basically, it just sets a global flag, and main() will
     exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used :return None"""
    # Your code here
    logger.warning('Received: ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def main(args):
    """ Stand alone function"""
    # Your code here
    # this function can only be called once.
    # %(asctime)s adds the time of creation of the LogRecord
    logging.basicConfig(
        format='%(process)d - %(asctime)s'
               '%(levelname)s - %(message)s',
        datefmt='%y-%m-%d &%H:%M:%S'
    )
    # using the level parameter, you can set what level
    # of log messages you want to record
    logger.setLevel(logging.DEBUG)
    start_time = time.time()
    logger.info(
        '\n' +
        '-' * 80 +
        f'\n\tRunning {__file__}\n' +
        f'\n\t Started on {start_time:.1f}\n' +
        '-' * 80 + '\n'
    )

    parser = create_parser()
    parsed_args = parser.parse_args(args)
    polling_interval = parsed_args.interval

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            # call my directory watching function
            watch_directory(
                parsed_args.path,
                parsed_args.magic_string,
                parsed_args.extension,
                float(parsed_args.interval)
                )
        # except clause determines how your program responds to exceptions.
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f'{parsed_args.path} path not found')
                time.sleep(2)
            else:
                logger.error(e)
        except Exception as e:
            # This is an UNHANDLED exception
            logger.error(f'UNHANDLED EXCEPTION:{e}')
            # Log an ERROR level message here
            # put sleep inside while loop so don't peg the cpu usage at 100%
        time.sleep(int(polling_interval))

    full_time = time.time() - start_time
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
    logger.info(
        '\n' +
        '-' * 80 +
        f'\n\tStopped {__file__}\n' +
        f'\n\tUptime was {full_time:.1f}\n' +
        '-' * 80 + '\n'
    )
    logging.shutdown()


if __name__ == '__main__':
    main(sys.argv[1:])
