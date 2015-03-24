#!/usr/bin/env python
# coding: utf-8

import ConfigParser

def loadSettings(filename):
	config = ConfigParser.ConfigParser()
	config.sections()
	config.read(filename)

	## Global
	global loglevel
	loglevel = config.getint('GLOBAL', 'Loglevel')

	## Mail
	global smtpAddress
	smtpAddress = config.get('MAIL', 'Server')

	global smtpPort
	smtpPort = config.getint('MAIL', 'Port')

	global smtpUser
	smtpUser = config.get('MAIL', 'User')

	global smtpPassword
	smtpPassword = config.get('MAIL', 'Password')

	global smtpSender
	smtpSender = config.get('MAIL', 'Sender')

	global adminMailAddress
	adminMailAddress = config.get('MAIL', 'AdminMail')

	## OX
	global ox_login_name
	ox_login_name = config.get('OX', 'User')

	global ox_login_pass
	ox_login_pass = config.get('OX', 'Password')

	global ox_login_url
	ox_login_url = config.get('OX', 'Login_URL')

	global ox_contacts_url
	ox_contacts_url = config.get('OX', 'Contacts_URL')

	global ox_contacts_folder
	ox_contacts_folder = config.get('OX', 'Contacts_folder')

	## OX contacts colums
	global ox_contacts_columns
	ox_contacts_columns = ""
	for key in config.items('OX_CONTACTS_COLUMNS'):
		ox_contacts_columns += key[1]
		ox_contacts_columns += ","

	## Redmine
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


