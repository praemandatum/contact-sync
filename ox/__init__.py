#!/usr/bin/env python
# coding: utf-8

import requests

from __contact_field_constants import *
import session
from ox.contacts import Contacts

class OX(object):

    def __init__(self, baseUrl, username, password):
        self.__session = session.OXSession(baseUrl, username, password)
        self.__session.establish()
        self.contacts = Contacts(self)


    def list(self, folder, columns):
        """Load all contacts."""
        payload = self.__build_request("all", folder, columns)
        res = self.__request(payload)
        return res.get("data")

    def list_since(self, since, folder, columns):
        """Load contacts that changed since given timestamp."""
        payload = self.__build_request("updates", folder, columns)
        payload["timestamp"] = since
        raw = self.__request(payload)
        return response.UpdatesResponse.parse(raw, columns)


    def create(self, folder, columns):
        """Create a contact."""


    def __build_request(self, action, folder, columns):
        return {
                'session': self.__session.token,
                'folder': folder,
                'columns': ",".join([str(c) for c in columns]),
                "action": action
                }

    def request(self, method, url, payload):
        r = getattr(requests, method)(urljoin(self.__session.baseUrl, url), params=payload,
                cookies=self.__session.cookie)

        if r.status_code != 200:
            raise Exception("Could not get OX contacts!\n" + r.text)

        # TODO: handle http errors here and return abstractions
        return json.loads(r.text)

