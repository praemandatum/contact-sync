#!/usr/bin/env python
# coding: utf-8

import requests
import json
import logging

import settings
from mail import send_error_mail_and_log


json_request_header = {'content-type': 'application/json'}


# Get all Redmine contacts
def get_all_redmine_contacts():
    payload = {'limit': 1000}  # Redmine limits the amount of contacts per request. Try to get as many as possible.
    r = requests.get(settings.redmine_url_contacts, params=payload,
                     auth=(settings.redmine_user, settings.redmine_password))

    if r.status_code != 200:
        send_error_mail_and_log(settings.admin_mail_address, "Could not get Redmine contacts!", True)

    contacts = json.loads(r.text)
    all_contacts = contacts["contacts"]

    while contacts["total_count"] > len(all_contacts):
        payload = {'limit': 1000, 'offset': len(all_contacts)}
        r = requests.get(settings.redmine_url_contacts, params=payload,
                         auth=(settings.redmine_user, settings.redmine_password))

        if r.status_code != 200:
            send_error_mail_and_log(settings.admin_mail_address, "Could not get Redmine contacts!", True)

        contacts = json.loads(r.text)
        all_contacts += contacts["contacts"]
    return all_contacts


# Search for contacts with keyword.
def search_redmine_contacts(keyword):
    all_contacts = []
    # Loop until no more results are returned.
    while True:
        payload = {'search': keyword, 'limit': 1000, 'offset': len(all_contacts)}
        r = requests.get(settings.redmine_url_contacts, params=payload,
                         auth=(settings.redmine_user, settings.redmine_password))

        if r.status_code != 200:
            send_error_mail_and_log(settings.admin_mail_address, "Could not search in Redmine!", True)

        contacts = json.loads(r.text)
        if len(contacts["contacts"]) == 0:
            break
        all_contacts += contacts["contacts"]
    return all_contacts


def get_json_payload_add_contact(ox_contact, redmine_contact):
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
            "background": get_background(ox_contact),
            "job_title": ox_contact[17],
            "tag_list": get_combined_tag_list(ox_contact, redmine_contact),
            "website": ox_contact[20],
            "custom_fields": [{"value": ox_contact[0], "name": settings.name_ox_uid, "id": settings.uid_field_id}]
        }
    }
    return json.dumps(payload)


def get_background(ox_contact):
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


def get_combined_tag_list(ox_contact, redmine_contact):
    tags = ox_contact[18]
    if ox_contact[19] is not None:
        tags += ","
        tags += ox_contact[19]
    if redmine_contact is not None:
        for redmine_tag in redmine_contact['tag_list']:
            tags += ","
            tags += redmine_tag
    return tags


def get_json_payload_add_company(company_name):
    payload = {
        "contact": {
            "project_id": settings.redmine_project,
            "first_name": company_name,
            "is_company": True
        }
    }
    return json.dumps(payload)


def process_contact(contact, redmine_contacts):
    # Try to find existing contact in Redmine
    contact_found = False
    custom_field_uid_found = False
    if len(redmine_contacts) != 0:
        # Search OX UID in Redmine custom field (Runtime: O(n))
        for redmine_contact in redmine_contacts:
            # Search UID custom field
            for custom_field in redmine_contact["custom_fields"]:
                if custom_field["name"] == settings.name_ox_uid:
                    # Custom field "uid" found
                    custom_field_uid_found = True
                    # Use empty UID if value is not set
                    uid = custom_field.get("value", "")
                    if uid == contact[0]:
                        # Contact found -> Update contact
                        contact_found = True
                        r = requests.put(settings.redmine_url_contacts_update + str(redmine_contact["id"]) + ".json",
                                         headers=json_request_header,
                                         data=get_json_payload_add_contact(contact, redmine_contact),
                                         auth=(settings.redmine_user, settings.redmine_password))
                        logging.info("Updating: " + "(id: " + str(redmine_contact["id"]) + ")")
                        break
        if not custom_field_uid_found:
            send_error_mail_and_log(settings.admin_mail_address,
                                    "Custom field 'uid' not found. Please add the custom field to "
                                    "Redmine CRM contacts!", True)

    if not contact_found:
        # Contact not found -> Create new contact
        logging.info("Creating contact: " + get_json_payload_add_contact(contact, None))
        r = requests.post(settings.redmine_url_contacts, headers=json_request_header,
                          data=get_json_payload_add_contact(contact, None),
                          auth=(settings.redmine_user, settings.redmine_password))

    # Check request status and notify on errors
    if r.status_code != 201 and r.status_code != 200:
        if r.status_code == 422:
            send_error_mail_and_log(settings.admin_mail_address,
                                    "Unprocessable Entity: " + get_json_payload_add_contact(contact,
                                                                                            None) + "\n" + r.text,
                                    False)
        else:
            send_error_mail_and_log(settings.admin_mail_address,
                                    "Could not create or update contact: "
                                    + get_json_payload_add_contact(contact, None) + "\n" + r.text,
                                    False)


def process_company(contact):
    # Process company fields from contacts
    if contact[13] != "":
        contacts = search_redmine_contacts(contact[13])

        # Check if company already exists
        company_found = False
        for c in contacts:
            if c["first_name"] == contact[13] and c.get("is_company", False) is True:
                company_found = True
                break

        # Create company if not existing
        if not company_found:
            logging.info("Creating company: " + get_json_payload_add_company(contact[13]))
            r = requests.post(settings.redmine_url_contacts, headers=json_request_header,
                              data=get_json_payload_add_company(contact[13]),
                              auth=(settings.redmine_user, settings.redmine_password))

            # Check request status and notify on errors
            if r.status_code != 201 and r.status_code != 200:
                if r.status_code == 422:
                    send_error_mail_and_log(settings.admin_mail_address,
                                            "Unprocessable Entity: " + get_json_payload_add_company(
                                                contact[13]) + "\n" + r.text, False)
                else:
                    send_error_mail_and_log(settings.admin_mail_address,
                                            "Could not create or update contact: " + get_json_payload_add_company(
                                                contact[13]) + "\n" + r.text, False)


def sanitize_contact(contact):
    # Sanitize OX output
    for field in range(1, 21):
        if contact[field] is None:
            contact[field] = ""

    # Redmine disallows empty first name -> Rewrite empty names
    if contact[1] == "":
        contact[1] = "-"

    # Replace country code "Deutschland" with "DE"
    if contact[12] == "Deutschland":
        contact[12] = "DE"
    return contact


# Write contacts to redmine
def write_contacts(contacts):
    redmine_contacts = get_all_redmine_contacts()
    for contact in contacts["data"]:
        contact = sanitize_contact(contact)
        process_contact(contact, redmine_contacts)
        process_company(contact)
