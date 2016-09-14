#!/usr/bin/env python
# coding: utf-8

import requests
import json
from urlparse import urljoin

import response

class OXContactSaver(object):

    def __init__(self, session, folder, columns):
        self.__session = session
        self.__folder = folder
        self.__columns = columns


    def loadUpdates(self, since):
        """Load contacts that changed since given timestamp."""
        payload = self.__build_request("updates")
        payload["timestamp"] = since
        raw = self.__request(payload)
        return response.UpdatesResponse.parse(raw, self.__columns)



    def load(self, since):
        """Load all contacts."""
        payload = self.__build_request("all")
        res = self.__request(payload)
        return res.get("data")


    def __build_request(self, action):
        return {
                'session': self.__session.token,
                'folder': self.__folder,
                'columns': ",".join([str(c) for c in self.__columns]),
                "action": action
                }

    def __request(self, payload):
        r = requests.get(urljoin(self.__session.baseUrl, "/ajax/contacts"), params=payload,
                cookies=self.__session.cookie)

        if r.status_code != 200:
            raise Exception("Could not get OX contacts!\n" + r.text)

        return json.loads(r.text)

