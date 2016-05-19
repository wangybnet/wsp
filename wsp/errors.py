# coding=utf-8

from .http import HttpError


class IgnoreRequest(Exception):
    pass


class ResponseNotMatch(Exception):
    pass


ERRORS = (HttpError, IgnoreRequest, ResponseNotMatch)
