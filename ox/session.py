import requests
import json
from urlparse import urljoin

LOGIN_PATH = "/ajax/login?action=login"
LOGOUT_PATH = "/ajax/login?action=logout"

class OXSession(object):

    def __init__(self, baseUrl, username, password):
        self.baseUrl = baseUrl
        self.__username = username
        self.__password = password
        self.cookie = None
        self.token = None

    def establish(self):
        data = {'name': self.__username, 'password': self.__password}
        r = requests.post(urljoin(self.baseUrl, LOGIN_PATH), data=data)
        if r.status_code != 200:
            raise Exception("Could not get OX login token!")

        session = json.loads(r.text)
        self.token = session.get("session")
        if self.token is None:
            raise Exception("Didn't receive session!\n" + r.text)
        self.cookie = r.cookies


    def logout(self):
        payload = {'session': self.token,}
        r = requests.get(urljoin(self.baseUrl, LOGOUT_PATH), params=payload, cookies=self.cookie)
        if r.status_code != 200:
            raise Exception("OX logout failed!\n" + r.text)

