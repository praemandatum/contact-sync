#!/usr/bin/env python
# coding: utf-8

import logging, sys, settings
from ox import getOXContacts
from redmine import writeContacts
from settings import loadSettings

def main(configPath):
	loadSettings(configPath)
	logging.basicConfig(level=settings.loglevel)
	ox_contacts = getOXContacts()
	writeContacts(ox_contacts)

if __name__ == '__main__': 
	import sys
	if len(sys.argv) == 2:
		main(str(sys.argv[1]))
	elif len(sys.argv) > 2:
		print 'Error: Need at most one argument (path to config file)'
	else:
		main('config.ini')

