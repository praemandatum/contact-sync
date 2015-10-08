import requests
import json
from urlparse import urljoin

LOGIN_PATH = "/ajax/login?action=login"

class OXSession(object):

    def __init__(self, baseUrl, username, password):
        self.baseUrl = baseUrl
        self.__username = username
        self.__password = password
        self.cookie = None
        self.token = None

    def establish(self):
        payload = {'name': self.__username, 'password': self.__password}
        r = requests.post(urljoin(self.baseUrl, LOGIN_PATH), params=payload)
        if r.status_code != 200:
            raise Exception("Could not get OX login token!")

        session = json.loads(r.text)
        self.token = session.get("session")
        if self.token is None:
            raise Exception("Didn't receive session!\n" + r.text)
        self.cookie = r.cookies

