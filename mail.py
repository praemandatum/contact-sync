#!/usr/bin/env python
# coding: utf-8

import logging, smtplib, sys, settings

def sendErrorMailAndLog(recipient, errorMessage, exitOnError):
	logging.error(errorMessage)
	try:
		smtp = smtplib.SMTP(settings.smtpAddress, settings.smtpPort)
		smtp.starttls()
		smtp.login(settings.smtpUser, settings.smtpPassword)
		message = ("From: OX Sync <" + settings.smtpSender + ">\n" +
					"To: <" + recipient + ">\n" +
					"Subject: OX Sync error!" + "\n" + 
					errorMessage)
		smtp.sendmail(settings.smtpSender, recipient, message)
	except:
		logging.error("Could not send mail!")

	if exitOnError == True:
		sys.exit(1)
