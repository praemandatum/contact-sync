#!/usr/bin/env python
# coding: utf-8

import requests
import json
import logging

import settings
from mail import send_error_mail_and_log


# Get all OpenXChange contacts
def get_ox_contacts(diff_timestamp=None):
    token = get_token(settings.ox_login_name, settings.ox_login_pass)

    payload = {'session': str(token[0].get("session", "")), 'folder': settings.ox_contacts_folder,
            'columns': settings.ox_contacts_columns, "action": "all"}
    if diff_timestamp is not None:
        logging.info("Fetching updates from OX")
        payload["action"] = "updates"
        payload["timestamp"] = diff_timestamp
    r = requests.get(settings.ox_contacts_url, params=payload, cookies=token[1])

    if r.status_code != 200:
        send_error_mail_and_log(settings.admin_mail_address, "Could not get OX contacts!\n" + r.text, True)

    logging.debug(r.text)
    return json.loads(r.text)


# Request OpenXChange token and cookie
def get_token(login_name, login_password):
    payload = {'name': login_name, 'password': login_password}
    r = requests.post(settings.ox_login_url, params=payload)

    if r.status_code != 200:
        send_error_mail_and_log(settings.admin_mail_address, "Could not get OX login token!", True)

    ox_session = json.loads(r.text)
    if ox_session.get("session", "") == "":
        send_error_mail_and_log(settings.admin_mail_address, "Didn't receive session!\n" + r.text, True)
    ox_cookie = r.cookies
    return ox_session, ox_cookie
