#!/usr/bin/env python
# coding: utf-8

import ConfigParser

def load_settings(filename):
    config = ConfigParser.ConfigParser()
    config.sections()
    config.readfp(filename)
    filename.close()

    # Global
    loglevel = config.getint('GLOBAL', 'Loglevel')
    global timestamp_file
    timestamp_file = config.get('GLOBAL', 'TimestampFile')

    # Mail
    global smtp_address
    smtp_address = config.get('MAIL', 'Server')

    global smtp_port
    smtp_port = config.getint('MAIL', 'Port')

    global smtp_user
    smtp_user = config.get('MAIL', 'User')

    global smtp_password
    smtp_password = config.get('MAIL', 'Password')

    global smtp_sender
    smtp_sender = config.get('MAIL', 'Sender')

    global admin_mail_address
    admin_mail_address = config.get('MAIL', 'AdminMail')

    # OX
    global ox_login_name
    ox_login_name = config.get('OX', 'User')

    global ox_login_pass
    ox_login_pass = config.get('OX', 'Password')

    global ox_base_url
    ox_base_url = config.get('OX', 'Base_URL')

    global ox_contacts_folder
    ox_contacts_folder = config.get('OX', 'Contacts_folder')

    # OX contacts colums
    global ox_contacts_columns
    ox_contacts_columns = ""
    for key in config.items('OX_CONTACTS_COLUMNS'):
        ox_contacts_columns += key[1]
        ox_contacts_columns += ","

    # Redmine
    global redmine_user
    redmine_user = config.get('REDMINE', 'User')

    global redmine_password
    redmine_password = config.get('REDMINE', 'Password')

    global redmine_project
    redmine_project = config.get('REDMINE', 'Project')

    global redmine_url
    redmine_url = config.get('REDMINE', 'Contacts_URL')


    global name_ox_uid
    name_ox_uid = config.get('REDMINE', 'Name_OX_UID')

    global uid_field_id
    uid_field_id = config.get('REDMINE', 'UID_field_id')

    global name_ox_website
    name_ox_website = config.get('REDMINE', 'Name_OX_Website')

    global ox_website_field_id
    ox_website_field_id = config.get('REDMINE', 'OX_Website_field_id')

