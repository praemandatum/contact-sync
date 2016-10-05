#!/usr/bin/env python
# coding: utf-8

from __contact_field_constants import *

class Contacts(object):

    def __init__(self, ox):
        self.ox = ox


    def list(self, folder, columns):
        """Load all contacts."""
        # TODO fix payload building
        payload = self.__build_request("all", folder, columns)
        res = self.ox.request("get", "/contacts?action=all", payload)
        return res.get("data")

    def list_since(self, since, folder, columns):
        """Load contacts that changed since given timestamp."""
        payload = self.__build_request("updates", folder, columns)
        payload["timestamp"] = since
        raw = self.ox.request("get", "/contacts?action=all", payload)
        return response.UpdatesResponse.parse(raw, columns)


    def create(self, folder, contact_data):
        """Create a contact."""
        payload = {
            'session': self.ox.__session.token,
            'body': contact_data,
        }
        r = self.ox.request("put", "/contacts?action=new", payload)

        if r.status_code != 200:
            raise Exception("Could not get OX contacts!\n" + r.text)

        return json.loads(r.text)


    def __build_request(self, action, folder, columns):
        return {
                'session': self.ox.__session.token,
                'folder': folder,
                'columns': ",".join([str(c) for c in columns]),
                "action": action
                }



    def fromRedmineContact(self, red_contact):
        c = dict()
        c["last_name"] = red_contact.last_name
        c["first_name"] = red_contact.first_name
        c["second_name"] = red_contact.middle_name
        #c["title"] = "" # titles are currently not supported by Redmine CRM

        # adopt phones
        if len(red_contact.phones) > 3:
            # TODO handle this more sensible
            raise Exception("More than 3 phone numbers are not supported by this script")
        if red_contact.phones:
            c["telephone_business1"] = red_contact.phones.pop()
        if red_contact.phones:
            c["telephone_business2"] = red_contact.phones.pop()
        if red_contact.phones:
            c["telephone_other"] = red_contact.phones.pop()

        # adopt email
        if len(red_contact.emails) > 3:
            # TODO handle this more sensible
            raise Exception("OX does not support more than 3 email addresses.")
        if red_contact.emails:
            c["email1"] = red_contact.emails.pop()
        if red_contact.emails:
            c["email2"] = red_contact.emails.pop()
        if red_contact.emails:
            c["email3"] = red_contact.emails.pop()

        # adopt address
        c["street_business"] = red_contact.address.get("street", "")
        c["postal_code_business"] = red_contact.address.get("postcode", "")
        c["city_business"] = red_contact.address.get("city", "")
        c["state_business"] = red_contact.address.get("region", "")
        c["country_business"] = red_contact.address.get("country", "")

        # misc
        c["company"] = red_contact.company
        c["position"] = red_contact.job_title
        c["url"] = red_contact.website

        return c
