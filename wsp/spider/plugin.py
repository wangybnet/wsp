# coding=utf-8

from wsp.plugin import PluginManager


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
        super(SpiderPluginManager, self)._add_plugin(plugin)
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
        # FIXME: Get plugin list from configuration

        plugin_list = ["wsp.spiderplugins.levellimit.LevelLimitPlugin"]
        return plugin_list
