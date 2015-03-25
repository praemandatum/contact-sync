#!/usr/bin/env python
# coding: utf-8

import requests, json, logging, settings
from mail import sendErrorMailAndLog

json_request_header = {'content-type': 'application/json'}

## Get all Redmine contacts
def getAllRedmineContacts():
	payload = {'limit': 1000} ## Redmine limits the amount of contacts per request. Try to get as many as possible.
	r = requests.get(settings.redmine_url_contacts, params=payload, auth=(settings.redmine_user, settings.redmine_password))

	if r.status_code != 200:
		sendErrorMailAndLog(settings.adminMailAddress, "Could not get Redmine contacts!", True)

	contacts = json.loads(r.text)
	all_contacts = contacts["contacts"]

	while contacts["total_count"] > len(all_contacts):
		payload = {'limit': 1000, 'offset': len(all_contacts)}
		r = requests.get(settings.redmine_url_contacts, params=payload, auth=(settings.redmine_user, settings.redmine_password))

		if r.status_code != 200:
			sendErrorMailAndLog(settings.adminMailAddress, "Could not get Redmine contacts!", True)

		contacts = json.loads(r.text)
		all_contacts += contacts["contacts"]
	return all_contacts

## Search for contacts with keyword. 
def searchRedmineContacts(keyword):
	all_contacts = []
	## Loop until no more results are returned.
	while True:
		payload = {'search': keyword, 'limit': 1000, 'offset': len(all_contacts)}
		r = requests.get(settings.redmine_url_contacts, params=payload, auth=(settings.redmine_user, settings.redmine_password))

		if r.status_code != 200:
			sendErrorMailAndLog(settings.adminMailAddress, "Could not search in Redmine!", True)

		contacts = json.loads(r.text)
		if len(contacts["contacts"]) == 0:
			break
		all_contacts += contacts["contacts"]
	return all_contacts

def getJsonPayloadAddContact(ox_contact, redmine_contact):
	payload = { 
	  "contact": {
		"project_id": settings.redmine_project,
		"first_name": ox_contact[1],
		"last_name": ox_contact[2],
		"middle_name": ox_contact[3],
		"phone": ox_contact[4],
		"email": ox_contact[5] + "," + ox_contact[6] + "," + ox_contact[7],
		"address_attributes": {
			"street1": ox_contact[8],
			"postcode": ox_contact[9],
			"city": ox_contact[10],
			"region": ox_contact[11],
			"country_code": ox_contact[12],
			},
		"company": ox_contact[13],
		"background": getBackground(ox_contact),
		"job_title": ox_contact[17],
		"tag_list": getCombinedTagList(ox_contact, redmine_contact),
		"custom_fields": [{"value": ox_contact[0], "name": settings.name_ox_uid, "id": settings.uid_field_id}]
	  }
	}
	return json.dumps(payload)

def getBackground(ox_contact):
	background = ox_contact[14]
	if background != "":
		background += ": "

	if ox_contact[15] != "":
		background += ox_contact[15]
		background += ": "

	if ox_contact[16] != "":
		background += "\n"
		background += ox_contact[16]
	return background

def getCombinedTagList(ox_contact, redmine_contact):
	tags = ox_contact[18]
	if redmine_contact != None:
		for redmine_tag in redmine_contact['tag_list']:
			tags += ","
			tags += redmine_tag
	return tags

def getJsonPayloadAddCompany(company_name):
	payload = { 
	  "contact": {
		"project_id": settings.redmine_project,
		"first_name": company_name,
		"is_company": True
	  }
	}
	return json.dumps(payload)

def processContact(contact, redmine_contacts):
	# Try to find existing contact in Redmine
	contact_found = False
	custom_field_uid_found = False
	if len(redmine_contacts) != 0:
		## Search OX UID in Redmine custom field (Runtime: O(n))
		for redmine_contact in redmine_contacts:
			## Search UID custom field
			for custom_field in redmine_contact["custom_fields"]:
				if custom_field["name"] == settings.name_ox_uid:
					## Custom field "uid" found
					custom_field_uid_found = True
					## Use empty UID if value is not set
					uid = custom_field.get("value", "")
					if uid == contact[0]:
						## Contact found -> Update contact
						contact_found = True
						r = requests.put(settings.redmine_url_contacts_update + str(redmine_contact["id"]) + ".json", headers=json_request_header, data=getJsonPayloadAddContact(contact, redmine_contact), auth=(settings.redmine_user, settings.redmine_password))
						logging.info("Updating: " + "(id: " + str(redmine_contact["id"]) + ")")
						break
		if custom_field_uid_found == False:
			sendErrorMailAndLog(settings.adminMailAddress, "Custom field 'uid' not found. Please add the custom field to Redmine CRM contacts!", True)

	if contact_found == False:
		## Contact not found -> Create new contact
		logging.info("Creating contact: " + getJsonPayloadAddContact(contact, None))
		r = requests.post(settings.redmine_url_contacts, headers=json_request_header, data=getJsonPayloadAddContact(contact, None), auth=(settings.redmine_user, settings.redmine_password))

	## Check request status and notify on errors
	if (r.status_code != 201 and r.status_code != 200):
		if r.status_code == 422:
			sendErrorMailAndLog(settings.adminMailAddress, "Unprocessable Entity: " + getJsonPayloadAddContact(contact, None) + "\n" + r.text, False)
		else:
			sendErrorMailAndLog(settings.adminMailAddress, "Could not create or update contact: " + getJsonPayloadAddContact(contact, None) + "\n" + r.text, False)

def processCompany(contact):
	## Process company fields from contacts
	if (contact[13] != ""):
		contacts = searchRedmineContacts(contact[13])

		## Check if company already exists
		companyFound = False
		for c in contacts:
			if c["first_name"] == contact[13] and c.get("is_company", False) == True:
				companyFound = True
				break;

		## Create company if not existing
		if companyFound == False:
			logging.info("Creating company: " + getJsonPayloadAddCompany(contact[13]))
			r = requests.post(settings.redmine_url_contacts, headers=json_request_header, data=getJsonPayloadAddCompany(contact[13]), auth=(settings.redmine_user, settings.redmine_password))

			## Check request status and notify on errors
			if (r.status_code != 201 and r.status_code != 200):
				if r.status_code == 422:
					sendErrorMailAndLog(settings.adminMailAddress, "Unprocessable Entity: " + getJsonPayloadAddCompany(contact[13]) + "\n" + r.text, False)
				else:
					sendErrorMailAndLog(settings.adminMailAddress, "Could not create or update contact: " + getJsonPayloadAddCompany(contact[13]) + "\n" + r.text, False)

def sanitizeContact(contact):
	## Sanitize OX output
	for field in range(1, 19):
		if contact[field] == None:
			contact[field] = ""

	## Redmine disallows empty first name -> Rewrite empty names
	if contact[1] == "":
		contact[1] = "-"
	return contact

## Write contacts to redmine
def writeContacts(contacts):
	redmine_contacts = getAllRedmineContacts()
	for contact in contacts["data"]:
		contact = sanitizeContact(contact)
		processContact(contact, redmine_contacts)
		processCompany(contact)
