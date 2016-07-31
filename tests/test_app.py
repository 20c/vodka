import unittest
import vodka.app

class AppA(vodka.app.Application):
    handle = "app_a"

class AppB(vodka.app.Application):
    handle = "app_b"


class TestApp(unittest.TestCase):

    def test_register(self):
        vodka.app.register(AppA)
        assert vodka.app.applications.get("app_a") == AppA
        with self.assertRaises(KeyError):
            vodka.app.register(AppA)


    def test_get_application(self):
        vodka.app.register(AppB)
        assert vodka.app.get_application("app_b") == AppB
        with self.assertRaises(KeyError):
            vodka.app.get_application("does_not_exist")

