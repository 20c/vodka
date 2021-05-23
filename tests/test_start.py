import os.path
import time
import unittest
import vodka
import vodka.plugins
import vodka.instance


@vodka.plugin.register('test_start_plugin_a')
class TimedPlugin(vodka.plugins.TimedPlugin):
    def init(self):
        self.counter = 0
        self.setup_done = False
    def setup(self):
        self.setup_done = True
    def work(self):
        self.counter += 1


HOME = os.path.join(os.path.dirname(__file__), "resources", "test_start_app")

CONFIG = {
    # applications for this test be loaded from resources/appdir/application.py
    "apps" : {
        "test_start_app" : {
            "home": HOME,
            "enabled" : True
        },
        "test_start_app_inactive" : {
            "home": HOME,
            "module" : "test_start_app.application",
            "enabled" : False
        }
    },
    "plugins" : [
        {
            "type" : "test_start_plugin_a",
            "name" : "test_start_plugin_a",
            "interval" : 0.1,
            "async" : "thread"
        },
        {
            "type" : "test_start_plugin_a",
            "name" : "test_start_plugin_b",
            "interval" : 0.1,
            "start_manual" : True
        }
    ]
}

class TestStart(unittest.TestCase):

    def test_init_and_start(self):
        r = vodka.init(CONFIG, CONFIG)

        # make sure plugin workers were assigned accordingly
        self.assertEqual(r, {
            "asyncio_workers" : [],
            "gevent_workers" : [],
            "thread_workers" : [vodka.plugin.get_instance("test_start_plugin_a")]
        })

        # make sure app was instantiated
        app = vodka.instance.get_instance("test_start_app")
        self.assertEqual(app.setup_done, True)

        # make sure inactive app was not instantiated
        with self.assertRaises(KeyError):
            vodka.instance.get_instance("test_start_app_inactive")

        # make sure skipped app was not instantiated
        with self.assertRaises(KeyError):
            vodka.instance.get_instance("test_start_app_skipped")

        # make sure plugin was setup
        plugin = vodka.plugin.get_instance("test_start_plugin_a")
        self.assertEqual(plugin.setup_done, True)

        vodka.start(**r)

        # give some time for startup to complete
        time.sleep(0.25)

        # make sure plugin is running
        self.assertEqual(plugin.run_level, 1)

        # make sure manually started plugin isnt running
        plugin = vodka.plugin.get_instance("test_start_plugin_b")
        self.assertEqual(hasattr(plugin, "run_level"), False)


