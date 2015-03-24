#!/usr/bin/env python
# coding: utf-8

import configparser

def loadSettings(filename):
	config = configparser.ConfigParser()
	config.sections()
	config.read(filename)

	## Global
	global loglevel
	loglevel = config.getint('GLOBAL', 'Loglevel')

	## Mail
	global smtpAddress
	smtpAddress = config['MAIL']['Server']

	global smtpPort
	smtpPort = config.getint('MAIL', 'Port')

	global smtpUser
	smtpUser = config['MAIL']['User']

	global smtpPassword
	smtpPassword = config['MAIL']['Password']

	global smtpSender
	smtpSender = config['MAIL']['Sender']

	global adminMailAddress
	adminMailAddress = config['MAIL']['AdminMail']

	## OX
	global ox_login_name
	ox_login_name = config['OX']['User']

	global ox_login_pass
	ox_login_pass = config['OX']['Password']

	global ox_login_url
	ox_login_url = config['OX']['Login_URL']

	global ox_contacts_url
	ox_contacts_url = config['OX']['Contacts_URL']

	global ox_contacts_folder
	ox_contacts_folder = config['OX']['Contacts_folder']

	## OX contacts colums
	global ox_contacts_columns
	ox_contacts_columns = ""
	for key in config['OX_CONTACTS_COLUMNS']:
		ox_contacts_columns += config['OX_CONTACTS_COLUMNS'][key]
		ox_contacts_columns += ","

	## Redmine
	global redmine_user
	redmine_user = config['REDMINE']['User']

	global redmine_password
	redmine_password = config['REDMINE']['Password']

	global redmine_project
	redmine_project = config['REDMINE']['Project']

	global redmine_url_contacts
	redmine_url_contacts = config['REDMINE']['Contacts_URL']

	global redmine_url_contacts_update
	redmine_url_contacts_update = config['REDMINE']['Contacts_update_URL']

	global name_ox_uid
	name_ox_uid = config['REDMINE']['Name_OX_UID']

	global uid_field_id
	uid_field_id = config['REDMINE']['UID_field_id']

