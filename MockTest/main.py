import os
import requests
from datetime import date


class Exception404(Exception):
    pass


class ProductionClass(object):

    def method(self, a, b, c):
        self.something(a, b, c)

    def something(self, a, b, c):
        print a, b, c

    def closer(self, something):
        something.close()

    def pid(self):
        return os.getpid()

    def iter(self):
        for i in xrange(0, 10):
            yield 1

    def empty(self):
        pass

    def request_test(self, url, data):
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception404('Request error')
        return response.content


class Response(object):

    def __init__(self, status, content):
        self.status_code = status
        self.content = content
