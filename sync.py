#!/usr/bin/env python
# coding: utf-8

import logging

import settings
from ox import get_ox_contacts
from redmine import write_contacts
from settings import load_settings


def main(config_path):
    load_settings(config_path)
    logging.basicConfig(level=settings.loglevel)
    ox_contacts = get_ox_contacts()
    write_contacts(ox_contacts)


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        main(str(sys.argv[1]))
    elif len(sys.argv) > 2:
        print 'Error: Need at most one argument (path to config file)'
    else:
        main('config.ini')