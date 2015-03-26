#!/usr/bin/env python
# coding: utf-8

import logging
import smtplib
import sys

import settings


def send_error_mail_and_log(recipient, error_message, exit_on_error):
    logging.error(error_message)
    try:
        smtp = smtplib.SMTP(settings.smtp_address, settings.smtp_port)
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        message = ("From: OX Sync <" + settings.smtp_sender + ">\n" +
                   "To: <" + recipient + ">\n" +
                   "Subject: OX Sync error!" + "\n" +
                   error_message)
        smtp.sendmail(settings.smtp_sender, recipient, message)
    except:
        logging.error("Could not send mail!")

    if exit_on_error:
        sys.exit(1)
