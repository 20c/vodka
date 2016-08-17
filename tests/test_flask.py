import unittest
import vodka
import vodka.plugins.wsgi
import vodka.config

from flask import Flask, request

class TestFlask(unittest.TestCase):
    
    @classmethod
    def setUp(cls):
        vodka.config.instance["home"] = "."
        cls.plugin = vodka.plugin.get_instance({
            "type" : "flask",
            "name" : "flask"
        })
     

    def test_init(self):
        self.assertEqual(isinstance(vodka.plugins.wsgi.application(), Flask), True)
    
    def test_request_env(self):
        env = self.plugin.request_env(something="else")
        self.assertEqual(
            {
                "request" : request,
                "static_url" : "/static/",
                "something" : "else"
            },
            env
        )

       
