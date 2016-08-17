import pluginmgr
import time
import urlparse

import vodka
import vodka.log
import vodka.config
import vodka.component
import vodka.data.handlers


def get_plugin_by_name(name):
    return vodka.plugin.get_instance(name)


def get_plugin_instance(name):
    return get_plugin_by_name(name)


def get_plugin_class(typ):
    return vodka.plugin.get_plugin_class(typ)


class PluginBase(vodka.component.Component, pluginmgr.PluginBase):

    class Configuration(vodka.component.Component.Configuration):
        async = vodka.config.Attribute(
            str,
            default="thread",
            choices=["thread", "gevent"],
            help_text="specifies how to run this plugin async"
        )
        type = vodka.config.Attribute(
            str,
            help_text="plugin registration type string"
        )
        name = vodka.config.Attribute(
            str,
            default=lambda x, i: i.type,
            help_text="plugin instance name, needs to be unique"
        )

    def init(self):
        """ executed during plugin initialization, app instances not available yet """
        pass

    def setup(self):
        """ executed before plugin is started, app instances available """
        pass

    def start(self):
        pass


class TimedPlugin(PluginBase):

    class Configuration(PluginBase.Configuration):
        interval = vodka.config.Attribute(
            float,
            help_text="minimum interval between calls to work method (in seconds)"
        )

    def sleep(self, n):
        if self.get_config("async") == "gevent":
            import gevent
            gevent.sleep(n)
        else:
            time.sleep(n)

    def start(self):
        self.run()

    def stop(self):
        self.run_level = 0

    def work(self):
        pass

    def run(self):
        self.run_level = 1
        interval = self.get_config("interval")
        while self.run_level:
            start = time.time()
            self.work()
            done = time.time()
            elapsed = done - start
            if elapsed <= interval:
                sleeptime = interval - elapsed
                if sleeptime > 0:
                    self.sleep(sleeptime)


class DataPlugin(TimedPlugin):

    """
    Plugin that allows to retrieve data from a source on an
    interval

    Don't instantiate this, but use as a base for other plugins.
    """

    class Configuration(TimedPlugin.Configuration):

        data = vodka.config.Attribute(
            str,
            help_text="specify the data type of data fetched by this plugin. Will also apply the vodka data handler with matching name if it exists"
        )

    @property
    def data_type(self):
        return self.get_config("data")

    def init(self):
        return

    def work(self, data):
        return vodka.data.handle(self.data_type, data, data_id=self.name, caller=self)

