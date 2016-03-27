# coding=utf-8


class DownloaderPluginManager:
    """
    下载器插件管理器

    插件由内向外逐层包裹下载器。
    """
    def __init__(self, *plugins):
        self._request_handlers = []
        self._response_handlers = []
        self._error_handlers = []
        for plugin in plugins:
            self._add_plugin(plugin)

    @classmethod
    def from_config(cls):
        # FIXME: Get plugins from configuration
        plugins = []
        return cls(*plugins)

    def _add_plugin(self, plugin):
        if hasattr(plugin, "handle_request"):
            self._request_handlers.append(plugin.handle_request)
        if hasattr(plugin, "handle_response"):
            self._response_handlers.append(plugin.handle_response)
        if hasattr(plugin, "handle_error"):
            self._error_handlers.append(plugin.handle_error)

    @property
    def request_handlers(self):
        return self._request_handlers

    @property
    def response_handlers(self):
        return self._response_handlers

    @property
    def error_handlers(self):
        return self._error_handlers
