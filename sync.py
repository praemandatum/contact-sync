#!/usr/bin/env python
# coding: utf-8

import logging
import pickle

import settings
from ox import get_ox_contacts
from redmine import write_contacts
from settings import load_settings

"""Reads the timestamp (seconds since epoc) of the last sync."""
def read_timestamp(path):
    try:
        with open(path, "r") as f:
            lastrun = pickle.load(f)
    except IOError as e:
        # this should only occur on the first run of this script
        # if the pickled timestamp is not present yet
        logging.info("Failed to read timestamp. " + e.args[1])
        lastrun = 0
    return lastrun

def save_timestamp(path, lastrun):
    with open(path, "w") as f:
        pickle.dump(lastrun, f)


def main(config_path):
    load_settings(config_path)
    logging.basicConfig(level=settings.loglevel)
    lastrun = read_timestamp(settings.timestamp_file)
    ox_contacts = get_ox_contacts(lastrun)
    if ox_contacts["data"]:
        write_contacts(ox_contacts)
    else:
        # no changes since last sync attempt
        # no need to write anything to redmine
        pass
    save_timestamp(settings.timestamp_file, ox_contacts["timestamp"])


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        main(str(sys.argv[1]))
    elif len(sys.argv) > 2:
        print 'Error: Need at most one argument (path to config file)'
    else:
        main('config.ini')
