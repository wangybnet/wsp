# coding=utf-8


class ProxyMiddleware:
    """
    给Http请求添加代理的中间件
    """
    def __init__(self, agent_addr):
        self._agent_addr = agent_addr

    """
    根据任务配置实例化代理中间件
    """
    @classmethod
    def from_config(cls, config):
        return cls(config.get("agent_addr"))

    """
    给请求添加代理
    """
    async def handle_request(self, request):
        # TODO
        pass

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