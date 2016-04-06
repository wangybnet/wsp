# coding=utf-8

from wsp.http.error import HttpError


class IgnoreRequest(Exception):
    pass


class AccessDeny(Exception):
    pass


class ResponseNotMatch(Exception):
    pass


ERRORS = (HttpError, IgnoreRequest, AccessDeny, ResponseNotMatch)
