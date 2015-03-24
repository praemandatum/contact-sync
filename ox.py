#!/usr/bin/env python
# coding: utf-8

import requests, json, settings
from mail import sendErrorMailAndLog

## Get all Openxchange contacts
def getOXContacts():
	token = getToken(settings.ox_login_name, settings.ox_login_pass)

	payload = {'session': str(token[0].get("session", "")), 'folder': settings.ox_contacts_folder, 'columns': settings.ox_contacts_columns}
	r = requests.get(settings.ox_contacts_url, params=payload, cookies=token[1]);

	if r.status_code != 200:
		sendErrorMailAndLog(settings.adminMailAddress, "Could not get OX contacts!\n" + r.text, True)

	return json.loads(r.text)

## Request Openxchange token and cookie
def getToken(login_name, login_password):
	payload = {'name': login_name, 'password': login_password}
	r = requests.post(settings.ox_login_url, params=payload)

	if r.status_code != 200:
		sendErrorMailAndLog(settings.adminMailAddress, "Could not get OX login token!", True)

	ox_session = json.loads(r.text)
	if ox_session.get("session", "") == "":
		sendErrorMailAndLog(settings.adminMailAddress, "Didn't receive session!\n" + r.text, True)
	ox_cookie = r.cookies
	return (ox_session, ox_cookie)
