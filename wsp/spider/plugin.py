# coding=utf-8


class SpiderPluginManager:
    """
    Spider插件管理器

    插件由内向外逐层包裹Spider。
    """
    def __init__(self, *plugins):
        self._input_handlers = []
        self._output_handlers = []
        self._error_handlers = []
        for plugin in plugins:
            self._add_plugin(plugin)

    @classmethod
    def from_config(cls, conf):
        # FIXME: Get plugins from configuration
        plugins = []
        return cls(*plugins)

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
