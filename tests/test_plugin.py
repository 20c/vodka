import unittest

import vodka.plugins
import vodka

@vodka.plugin.register('test')
class PluginA(vodka.plugins.PluginBase):
    pass

class TestPlugin(unittest.TestCase):
   
    def test_get_plugin_by_name(self):
        expected = vodka.plugin.get_instance({"type":"test", "name":"a"})
        plugin = vodka.plugins.get_plugin_by_name("a")
        self.assertEqual(plugin, expected)

    def test_get_plugin_class(self):
        self.assertEqual(PluginA, vodka.plugins.get_plugin_class("test"))
        

