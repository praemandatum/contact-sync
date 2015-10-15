#!/usr/bin/env python
# coding: utf-8

import logging
import smtplib
import sys


def send_error_mail_and_log(config, recipient, error_message, exit_on_error):
    logging.error(error_message)
    try:
        smtp = smtplib.SMTP(config.get("MAIL", "Server"), config.get("MAIL", "Port"))
        smtp.starttls()
        smtp.login(config.get("MAIL", "User"), config.get("MAIL", "Password"))
        message = ("""From: OX Sync <{sender}>
To: <{recipient}>
Subject: OX Sync error!

{message}
""".format(
            sender=config.get("MAIL", "Sender"),
            recipient=recipient,
            message=error_message))
        smtp.sendmail(config.get("MAIL", "Sender"), recipient, message)
    except:
        logging.error("Could not send mail!")

    if exit_on_error:
        sys.exit(1)
