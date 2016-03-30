# coding=utf-8

from wsp.plugin import PluginManager
from wsp.config import task as tc


class SpiderPluginManager(PluginManager):
    """
    Spider插件管理器
    """

    def __init__(self, *plugins):
        self._input_handlers = []
        self._output_handlers = []
        self._error_handlers = []
        super(SpiderPluginManager, self).__init__(*plugins)

    def _add_plugin(self, plugin):
        if hasattr(plugin, "handle_input"):
            self._input_handlers.append(plugin.handle_input)
        if hasattr(plugin, "handle_output"):
            self._output_handlers.append(plugin.handle_output)
        if hasattr(plugin, "handle_error"):
            self._error_handlers.append(plugin.handle_error)

    @property
    def input_handlers(self):
        return self._input_handlers

    @property
    def output_handlers(self):
        return self._output_handlers

    @property
    def error_handlers(self):
        return self._error_handlers

    @classmethod
    def _plugin_list_from_config(cls, config):
        return config.get(tc.SPIDER_PLUGINS)
