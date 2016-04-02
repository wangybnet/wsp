# coding=utf-8


class HttpError(Exception):
    def __init__(self, error):
        self.error = error
        super(HttpError, self).__init__(error)
