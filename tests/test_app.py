import unittest
import vodka.app

@vodka.app.register('app_a')
class AppA(vodka.app.Application):
    pass

@vodka.app.register('app_b')
class AppB(vodka.app.Application):
    pass


class TestApp(unittest.TestCase):

    def test_register(self):
        vodka.app.register(AppA)
        assert vodka.app.applications.get("app_a") == AppA
        with self.assertRaises(KeyError):
            @vodka.app.register('app_a')
            class AppC(vodka.app.Application):
                pass


    def test_get_application(self):
        vodka.app.register(AppB)
        assert vodka.app.get_application("app_b") == AppB
        with self.assertRaises(KeyError):
            vodka.app.get_application("does_not_exist")

