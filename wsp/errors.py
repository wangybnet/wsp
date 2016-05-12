# coding=utf-8

from .http import HttpError


class IgnoreRequest(Exception):
    pass


class AccessDeny(Exception):
    pass


class ResponseNotMatch(Exception):
    pass


ERRORS = (HttpError, IgnoreRequest, AccessDeny, ResponseNotMatch)
