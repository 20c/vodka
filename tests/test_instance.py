import unittest

import vodka.app
import vodka.instance

@vodka.app.register('app_a2')
class AppA(vodka.app.Application):
    initialized = False

    def setup(self):
        self.initialized = True

@vodka.app.register('app_b2')
class AppB(vodka.app.Application):
    pass

@vodka.app.register("app_versioned")
class AppV(vodka.app.WebApplication):
    version = "1.0.0"

APP_CONFIG = {
    "apps" : {
        AppA.handle : { "enabled" : True },
        AppB.handle : { "enabled" : False },
        AppV.handle : { "enabled" : True },
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

    def test_app_versioning(self):
        vodka.instance.instantiate(APP_CONFIG)

        inst_a = vodka.instance.get_instance(AppA.handle)
        inst_v = vodka.instance.get_instance(AppV.handle)

        self.assertEqual(inst_v.versioned_handle(), "app_versioned/1.0.0")
        self.assertEqual(inst_v.versioned_path("app_versioned/b/c"), "app_versioned/1.0.0/b/c")
        self.assertEqual(inst_v.versioned_url("app_versioned/b/c"), "app_versioned/b/c?v=1.0.0")


        self.assertEqual(inst_a.versioned_handle(), "app_a2")
