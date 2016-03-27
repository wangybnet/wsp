# coding=utf-8


class ProxyPlugin:
    def __init__(self, server_addr):
        self._server_addr = server_addr

    """
    根据任务配置实例化代理插件
    """
    @classmethod
    def from_task_config(cls, conf):
        pass

    """
    给请求添加代理
    """
    async def handle_request(self, request):
        # TODO
        return request

    """
    请求正常时的反馈
    """
    async def handle_response(self, request, response):
        # TODO
        pass

    """
    请求异常时的反馈
    """
    async def handle_error(self, request, error):
        # TODO
        pass
