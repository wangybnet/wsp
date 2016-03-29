# coding=utf-8

import logging

from wsp.utils.config import load_object

log = logging.getLogger(__name__)


class PluginManager:

    def __init__(self, *plugins):
        self._open_handlers = []
        self._close_handlers = []
        for plugin in plugins:
            self._add_plugin(plugin)

    @classmethod
    def _plugin_list_from_config(cls, config):
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        plugin_list = cls._plugin_list_from_config(config)
        plugins = []
        for cls_path in plugin_list:
            try:
                plugin_cls = load_object(cls_path)
                if hasattr(plugin_cls, "from_config"):
                    plugin = plugin_cls.from_config(config)
                else:
                    plugin = plugin_cls()
                plugins.append(plugin)
            except Exception as e:
                log.warning("An error occurred when loading plugin '%s': %s" % (cls_path, e))
        return cls(*plugins)

    def _add_plugin(self, plugin):
        if hasattr(plugin, "open"):
            self._open_handlers.append(plugin.open)
        if hasattr(plugin, "close"):
            self._close_handlers.append(plugin.close)

    @property
    def open_handlers(self):
        return self._open_handlers

    @property
    def close_handlers(self):
        return self._close_handlers

    def open(self):
        for h in self.open_handlers:
            h()

    def close(self):
        for h in self.close_handlers:
            h()
