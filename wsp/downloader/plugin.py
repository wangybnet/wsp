# coding=utf-8

from wsp.plugin import PluginManager


class DownloaderPluginManager(PluginManager):
    """
    下载器插件管理器
    """

    def __init__(self, *plugins):
        self._request_handlers = []
        self._response_handlers = []
        self._error_handlers = []
        super(DownloaderPluginManager, self).__init__(*plugins)

    def _add_plugin(self, plugin):
        super(DownloaderPluginManager, self)._add_plugin(plugin)
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

    @classmethod
    def _plugin_list_from_config(cls, config):
        # FIXME: Get plugin list from configuration

        plugin_list = ["wsp.downloaderplugins.check.CheckPlugin",
                       "wsp.downloaderplugins.retry.RetryPlugin",
                       "wsp.downloaderplugins.check.CheckPlugin",
                       "wsp.downloaderplugins.dump.DumpPlugin",
                       "wsp.downloaderplugins.persistence.PersistencePlugin"]
        return plugin_list
