import unittest
import vodka.config
import vodka.config.configurator
import sys

class Handler(vodka.config.Handler):
    a = vodka.config.Attribute(str)
    b = vodka.config.Attribute(str, default="something")
    c = vodka.config.Attribute(list, default=[])
    d = vodka.config.Attribute(dict, default={})
    e = vodka.config.Attribute(dict, default={})
    f = vodka.config.Attribute(dict, help_text="manually")

    @classmethod
    def configure_e(cls, configurator, cfg, path):
        _cfg = {}
        configurator.configure(_cfg, HandlerE, path="%s.%s"%(path,"test"))
        cfg["e"] = {"test":_cfg}


class HandlerE(vodka.config.Handler):
    a = vodka.config.Attribute(str)
    b = vodka.config.Attribute(str, default="else")

class Configurator(vodka.config.configurator.Configurator):
    def set_values(self, **kwargs):
        self.prompt_values = kwargs

    def prompt(self, k, default=None, *args, **kwargs):
        return self.prompt_values.get(k, default)

class TestConfigurator(unittest.TestCase):

    def test_configurator(self):
        configurator = Configurator(None)

        cfg = {}
        configurator.set_values(**{
            "a" : "what",
            "b" : "something",
            "c" : "nope",
            "d" : "nope",
            "e.test.a" : "who"
        })
        configurator.configure(cfg, Handler)
        self.assertEqual(cfg, {
            "a" : "what",
            "b" : "something",
            "e" : {
                "test" : {
                    "a" : "who",
                    "b" : "else"
                }
            }
        })

        self.assertEqual(configurator.action_required, [
            "f: manually"
        ])


    def test_configurator_skip_defaults(self):
        configurator = Configurator(None, skip_defaults=True)

        cfg = {}
        configurator.set_values(**{
            "a" : "what",
            "b" : "other",
            "c" : "nope",
            "d" : "nope",
            "e.test.a" : "who",
            "e.test.b" : "where"
        })
        configurator.configure(cfg, Handler)
        self.assertEqual(cfg, {
            "a" : "what",
            "b" : "something",
            "e" : {
                "test" : {
                    "a" : "who",
                    "b" : "else"
                }
            }
        })


    def test_configurator_override_defaults(self):
        configurator = Configurator(None)

        cfg = {}
        configurator.set_values(**{
            "a" : "what",
            "b" : "other",
            "c" : "nope",
            "d" : "nope",
            "e.test.a" : "who",
            "e.test.b" : "where"
        })
        configurator.configure(cfg, Handler)
        self.assertEqual(cfg, {
            "a" : "what",
            "b" : "other",
            "e" : {
                "test" : {
                    "a" : "who",
                    "b" : "where"
                }
            }
        })

    def test_configurator_skip_existing(self):
        configurator = Configurator(None)

        cfg = {"a":"why"}
        configurator.set_values(**{
            "a" : "what",
            "b" : "other",
            "c" : "nope",
            "d" : "nope",
            "e.test.a" : "who",
            "e.test.b" : "where"
        })
        configurator.configure(cfg, Handler)
        self.assertEqual(cfg, {
            "a" : "why",
            "b" : "other",
            "e" : {
                "test" : {
                    "a" : "who",
                    "b" : "where"
                }
            }
        })


