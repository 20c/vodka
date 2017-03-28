import unittest
import vodka
import vodka.app
import vodka.instance
import vodka.plugins.wsgi
import vodka.config

from flask import Flask, request

@vodka.app.register('flask_test')
class App(vodka.app.Application):

    def index(self):
        return "nothing"

    def crossdomain_test(self):
        return "crossdomain_test: nothing"

    def crossdomain_test_2(self):
        return "crossdomain_test: nothing"

    def crossdomain_test_3(self):
        return "crossdomain_test: nothing"



vodka.instance.instantiate(
    {
        "apps" : {
            "flask_test" : {
                "enabled" : True
            }
        }
    }
)

FLASK_PLUGIN = vodka.plugin.get_instance({
    "type" : "flask",
    "name" : "flask",
    "routes" : {
        "/" : "flask_test->index",

        "/crossdomain_test" : {
            "target" : "flask_test->crossdomain_test",
            "methods" : ["GET","OPTIONS"],
            "crossdomain" : {
                "origin" : "*"
            }
        },

        "/crossdomain_test_2" : {
            "target" : "flask_test->crossdomain_test_2",
            "methods" : ["GET", "OPTIONS"],
            "crossdomain" : {
                "origin" : ["a.com", "b.com"],
                "methods" : "GET, OPTIONS",
                "headers" : "Test-Header"
            }
        },


        "/crossdomain_test_3" : {
            "target" : "flask_test->crossdomain_test_3",
            "methods" : ["GET", "POST", "OPTIONS"],
            "crossdomain" : {
                "origin" : ["a.com", "b.com"],
                "methods" : ["GET"],
                "headers" : ["Another-Header", "Test-Header"]
            }
        }


    }
})

FLASK_PLUGIN.setup()
FLASK_APP = FLASK_PLUGIN.wsgi_application
FLASK_APP.config["TESTING"] = True

class TestFlask(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.flask_app = FLASK_APP
        cls.plugin = FLASK_PLUGIN
        cls.client = FLASK_APP.test_client()

    def test_init(self):
        self.assertEqual(isinstance(vodka.plugins.wsgi.application(), Flask), True)

    def test_request_env(self):
        with self.flask_app.test_request_context('/'):
            env = self.plugin.request_env(something="else")
            self.assertEqual(env.get("something"), "else")
            self.assertEqual(env.get("request"), request)
            self.assertEqual(env.get("host"), "http://localhost")
            self.assertEqual(env.get("flask_test"), {
                "static_url":"/static/flask_test/",
                "instance" : vodka.instance.get_instance("flask_test")
            })


    def _test_routing(self):
        self.assertEqual(self.client.get("/").data, "nothing")

    def test_crossdomain_decorator(self):
        rv = self.client.get("/crossdomain_test", follow_redirects=True)
        self.assertEqual(rv.data, b"crossdomain_test: nothing")
        self.assertEqual(rv.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(
            sorted(rv.headers.get("Access-Control-Allow-Methods").split(", ")),
            ["GET", "HEAD", "OPTIONS"]
        )

        rv = self.client.get("/crossdomain_test_2", follow_redirects=True)
        self.assertEqual(rv.data, b"crossdomain_test: nothing")
        self.assertEqual(rv.headers.get("Access-Control-Allow-Origin"), "a.com, b.com")
        self.assertEqual(
            sorted(rv.headers.get("Access-Control-Allow-Methods").split(", ")),
            ["GET", "OPTIONS"]
        )


        rv = self.client.get("/crossdomain_test_3", follow_redirects=True)
        self.assertEqual(rv.data, b"crossdomain_test: nothing")
        self.assertEqual(rv.headers.get("Access-Control-Allow-Origin"), "a.com, b.com")
        self.assertEqual(rv.headers.get("Access-Control-Allow-Headers"), "ANOTHER-HEADER, TEST-HEADER")
        self.assertEqual(
            sorted(rv.headers.get("Access-Control-Allow-Methods").split(", ")),
            ["GET"]
        )


