import json


class GithubException(Exception):
    def __init__(self, status, data):
        Exception.__init__(self)
        self.__status = status
        self.__data = data
        self.args = (status, data)

    @property
    def status(self):
        return self.__status

    @property
    def data(self):
        return self.__data

    def __str__(self):
        return "{status} {data}".format(status=self.status, data=json.dumps(self.data))


class RateLimitExceededException(GithubException):
    pass
