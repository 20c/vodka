import unittest
import vodka.plugins.wsgi
import vodka.config
import vodka.app
import vodka

@vodka.plugin.register('wsgi_test')
class WSGIPlugin(vodka.plugins.wsgi.WSGIPlugin):
    routes = {}

    def set_route(self, path, target, methods=None):
        self.routes[path] = {"target":target, "methods":methods or []}

@vodka.app.register('wsgi_test_app')
class WSGIApp(vodka.app.Application):

    def a(self):
        return "a"

    def b(self):
        return "b"

class TestWSGI(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.plugin = vodka.plugin.get_instance({
            "type" : "wsgi_test"
        })
        cls.plugin_2  = vodka.plugin.get_instance({
            "routes" : {
                "/a" : "wsgi_test_app->a",
                "/b" : {
                    "target" : "wsgi_test_app->b",
                    "methods" : ["GET", "POST"]
                }
            },
            "type" : "wsgi_test",
            "name" : "wsgi_test2"
        })
        vodka.instance.instantiate({
            "apps" : {
                "wsgi_test_app" : {
                    "home" : ".",
                    "enabled" : True
                }
            }
        })
        cls.app = vodka.instance.get_instance("wsgi_test_app")


    def test_default_config(self):
        self.assertEqual(self.plugin.get_config('debug'), False)
        self.assertEqual(self.plugin.get_config('host'), "localhost")
        self.assertEqual(self.plugin.get_config('port'), 80)
        self.assertEqual(self.plugin.get_config('static_url_path'), '/static')
        self.assertEqual(self.plugin.get_config('server'), 'self')
        self.assertEqual(self.plugin.get_config('routes'), {})

    def test_set_wsgi_app(self):
        app = object()
        self.plugin.set_wsgi_app(app)
        self.assertEqual(WSGIPlugin.wsgi_application, app)

    def test_request_env(self):
        req = object()
        self.plugin.setup()
        env = self.plugin.request_env(req=req, something="other")
        self.assertEqual(env["wsgi_test_app"], {
            "static_url" : "/static/wsgi_test_app/",
            "instance" : self.app
        })
        self.assertEqual(env["request"], req)
        self.assertEqual(env["something"], "other")


    def test_set_routes(self):
        self.plugin_2.set_routes()
        self.assertEqual(self.plugin_2.routes, {
            "/a" : { "target" : self.app.a, "methods" : ["GET"] },
            "/b" : { "target" : self.app.b, "methods" : ["GET","POST"] }
        })


