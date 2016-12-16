import unittest
import time

import vodka.plugins
import vodka.data
import vodka.storage
import vodka

@vodka.plugin.register('test')
class PluginA(vodka.plugins.PluginBase):
    pass

@vodka.plugin.register('timed_test')
class TimedPlugin(vodka.plugins.TimedPlugin):
    def init(self):
        self.counter = 0

    def work(self):
        self.counter += 1

@vodka.plugin.register('data_test')
class DataPlugin(vodka.plugins.DataPlugin):

    def work(self):
        data = {"data":[], "ts" : time.time()}
        return super(DataPlugin, self).work(data)

class TestPlugin(unittest.TestCase):

    def test_get_plugin_by_name(self):
        expected = vodka.plugin.get_instance({"type":"test", "name":"a"})
        plugin = vodka.plugins.get_plugin_by_name("a")
        self.assertEqual(plugin, expected)

    def test_get_plugin_class(self):
        self.assertEqual(PluginA, vodka.plugins.get_plugin_class("test"))


class TestTimedPlugin(unittest.TestCase):

    def test_run(self):
        plugin = vodka.plugin.get_instance({
            "type" : "timed_test",
            "interval" : 0.01
        })
        vodka.start(thread_workers=[plugin])
        time.sleep(0.05)
        plugin.stop()

        self.assertGreater(plugin.counter, 3)
        self.assertLess(plugin.counter, 7)


class TestDataPlugin(unittest.TestCase):

    def test_run(self):
        vodka.data.data_types.instantiate_from_config(
        [{
            "type" : "data_test",
            "handlers" : [
                {
                    "type" : "store",
                    "container" : "list",
                    "limit" : 10
                }
             ]
        }]
)

        plugin = vodka.plugin.get_instance({
            "type" : "data_test",
            "interval" : 0.01,
            "data" : "data_test"
        })

        vodka.start(thread_workers=[plugin])

        time.sleep(0.3)

        self.assertEqual(len(vodka.storage.get("data_test")), 10)
        for item in vodka.storage.get("data_test"):
            self.assertEqual("data" in item, True)
            self.assertEqual("ts" in item, True)


