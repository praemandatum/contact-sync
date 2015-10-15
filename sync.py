#!/usr/bin/env python
# coding: utf-8

import logging
import pickle
import optparse
import ConfigParser

import syncer
from mail import send_error_mail_and_log

def read_timestamp(path):
    """Reads the timestamp (seconds since epoc) of the last sync."""
    try:
        with open(path, "r") as f:
            lastrun = pickle.load(f)
    except IOError as e:
        # this should only occur on the first run of this script
        # if the pickled timestamp is not present yet
        logging.error("Failed to read timestamp. " + e.args[1])
        lastrun = 0
    return lastrun

def save_timestamp(path, lastrun):
    with open(path, "w") as f:
        pickle.dump(lastrun, f)

def main(args):
    try:
        config = ConfigParser.ConfigParser()
        config.sections()
        config.readfp(args.config)
        args.config.close()
        logging.basicConfig(level=config.getint('GLOBAL', 'Loglevel'))
        if config.getboolean("REDMINE", "CRMLight"):
            cls = syncer.ContactSyncerForLight
        else:
            cls = syncer.ContactSyncer
        logging.debug("Use syncer " + str(cls))
        sync = cls(
            ox_base=config.get('OX', 'URL'),
            ox_user=config.get('OX', 'User'),
            ox_password=config.get('OX', 'Password'),
            ox_folder=config.get('OX', 'Contacts_folder'),
            ox_columns=[c for c in ",".join([key[1] for key in config.items('OX_CONTACTS_COLUMNS')]).split(",")],
            redmine_base=config.get('REDMINE', 'URL'),
            redmine_key=config.get('REDMINE', 'Key'),
            redmine_project=config.get('REDMINE', 'Project'),
            redmine_cf_id=config.getint('REDMINE', 'ID_field_id'),
            redmine_cf_uid=config.getint('REDMINE', 'UID_field_id'),
            redmine_cf_oxurl=config.getint('REDMINE', 'OXURL_field_id')
        )
        sync.no_act = args.no_act
        lastrun = read_timestamp(config.get('GLOBAL', 'TimestampFile'))
        timestamp = sync.sync(lastrun)
        if timestamp != 0:
            save_timestamp(config.get('GLOBAL', 'TimestampFile'), timestamp)
    except Exception as e:
        send_error_mail_and_log(config.get("MAIL", "AdminMail"), str(e), True)



if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Sync OX contacts with redmine.')
    parser.add_argument('-c', '--config', dest='config', default='config.ini',
        type=argparse.FileType("r"), help='path to config file')
    parser.add_argument('-n', '--no-act', dest='no_act', action='store_true',
        help='do not actually sync')
    args = parser.parse_args()

    main(args)
