#!/usr/bin/env python
# coding: utf-8

import ConfigParser

loglevel = None
smtp_address = None
smtp_port = None
smtp_user = None
smtp_password = None
smtp_sender = None
admin_mail_address = None
ox_login_name = None
ox_login_pass = None
ox_login_url = None
ox_base_url = None
ox_contacts_url = None
ox_contacts_folder = None
ox_contacts_columns = None
redmine_user = None
redmine_password = None
redmine_project = None
redmine_url_contacts = None
redmine_url_contacts_update = None
name_ox_uid = None
name_ox_website = None
uid_field_id = None
ox_website_field_id = None


def load_settings(filename):
    config = ConfigParser.ConfigParser()
    config.sections()
    config.read(filename)

    # Global
    global loglevel
    loglevel = config.getint('GLOBAL', 'Loglevel')

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

    global ox_login_url
    ox_login_url = config.get('OX', 'Login_URL')

    global ox_base_url
    ox_base_url = config.get('OX', 'Base_URL')

    global ox_contacts_url
    ox_contacts_url = config.get('OX', 'Contacts_URL')

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

    global redmine_url_contacts
    redmine_url_contacts = config.get('REDMINE', 'Contacts_URL')

    global redmine_url_contacts_update
    redmine_url_contacts_update = config.get('REDMINE', 'Contacts_update_URL')

    global name_ox_uid
    name_ox_uid = config.get('REDMINE', 'Name_OX_UID')

    global uid_field_id
    uid_field_id = config.get('REDMINE', 'UID_field_id')

    global name_ox_website
    name_ox_website = config.get('REDMINE', 'Name_OX_Website')

    global ox_website_field_id
    ox_website_field_id = config.get('REDMINE', 'OX_Website_field_id')

