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


    def request(self, method, url, payload, params={}, body=None):
        params["session"] = self.__session.token
        kwargs = dict()
        if body:
            kwargs["data"] = body
        r = getattr(requests, method)(urljoin(self.__session.baseUrl, url), params=params,
                cookies=self.__session.cookie, **kwargs)

        if r.status_code != 200:
            raise Exception("Could not get OX contacts!\n" + r.text)

        # TODO: handle http errors here and return abstractions
        return json.loads(r.text)

