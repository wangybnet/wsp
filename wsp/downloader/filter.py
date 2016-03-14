# coding=utf-8


class RequestFilter:

    async def filter(self, request):
        raise NotImplementedError


class ResponseFilter:

    async def filter(self, request, response):
        raise NotImplementedError


class ErrorFilter:

    async def filter(self, request, error):
        raise NotImplementedError
