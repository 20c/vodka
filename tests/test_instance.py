import unittest

import vodka.app
import vodka.instance

class AppA(vodka.app.Application):
    handle = "app_a2"
    initialized = False

    def setup(self):
        self.initialized = True
vodka.app.register(AppA)

class AppB(vodka.app.Application):
    handle = "app_b2"
vodka.app.register(AppB)

APP_CONFIG = {
    "apps" : {
        AppA.handle : { "enabled" : True },
        AppB.handle : { "enabled" : False }
    }
}


class TestInstance(unittest.TestCase):

    def test_instantiate(self):
        vodka.instance.instantiate(APP_CONFIG)

        inst_a = vodka.instance.get_instance(AppA.handle)
        self.assertEqual(inst_a.handle, AppA.handle)

        with self.assertRaises(KeyError):
            vodka.instance.get_instance(AppB.handle)

    def test_setup(self):
        vodka.instance.instantiate(APP_CONFIG)

        inst_a = vodka.instance.get_instance(AppA.handle)

        vodka.instance.ready()

        self.assertEqual(inst_a.initialized, True)
 
