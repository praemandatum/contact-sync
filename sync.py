#!/usr/bin/env python
# coding: utf-8

import logging
import logging.handlers
import pickle
import optparse
import ConfigParser

import syncer

def read_timestamp(path):
    """Reads the timestamp (seconds since epoc) of the last sync."""
    try:
        with open(path, "r") as f:
            lastrun = pickle.load(f)
    except IOError as e:
        # this should only occur on the first run of this script
        # if the pickled timestamp is not present yet
        logging.warning("Failed to read timestamp. %s", e.args[1])
        lastrun = 0
    return lastrun

def save_timestamp(path, lastrun):
    with open(path, "w") as f:
        pickle.dump(lastrun, f)

def setup_logging(config):
    logging.basicConfig(level=config.getint('GLOBAL', 'Loglevel'))
    logger = logging.getLogger()
    smtp_handler = logging.handlers.SMTPHandler(
        mailhost=(config.get("MAIL", "Server"), config.get("MAIL", "Port")),
        fromaddr=config.get("MAIL", "Sender"),
        toaddrs=config.get("MAIL", "AdminMail"),
        subject="OX Sync error!",
        credentials=(config.get("MAIL", "User"), config.get("MAIL", "Password")),
        secure=()
    )
    smtp_handler.setLevel(logging.ERROR)
    logger.addHandler(smtp_handler)

def main(args):
    try:
        config = ConfigParser.ConfigParser()
        config.sections()
        config.readfp(args.config)
        args.config.close()
        setup_logging(config)
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
            redmine_base=config.get('REDMINE', 'URL'),
            redmine_key=config.get('REDMINE', 'Key'),
            redmine_project=config.get('REDMINE', 'Project'),
            redmine_cf_id=config.getint('REDMINE', 'ID_field_id'),
            redmine_cf_uid=config.getint('REDMINE', 'UID_field_id'),
            redmine_cf_oxurl=config.getint('REDMINE', 'OXURL_field_id')
        )
        sync.no_act = args.no_act
        lastrun = read_timestamp(config.get('GLOBAL', 'TimestampFile'))
        if args.force:
            timestamp = sync.sync()
        else:
            timestamp = sync.sync(lastrun)
        if timestamp != 0 and not sync.no_act:
            save_timestamp(config.get('GLOBAL', 'TimestampFile'), timestamp)
    except Exception as e:
        logging.exception(e)



if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Sync OX contacts with redmine.')
    parser.add_argument('-c', '--config', dest='config', default='config.ini',
        type=argparse.FileType("r"), help='path to config file')
    parser.add_argument('-n', '--no-act', dest='no_act', action='store_true',
        help='do not actually sync')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
        help='ignore timestamp and request all changes since epoc')
    args = parser.parse_args()

    main(args)
