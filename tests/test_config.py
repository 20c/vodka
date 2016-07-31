import unittest
import vodka.config
import vodka.exceptions as exc


def validator(value):
    return value < 5, "needs to be smaller than 5"

class ConfigHandler(vodka.config.Handler):
    a = vodka.config.Attribute(int, default=1, help_text="ht:a")
    b = vodka.config.Attribute(int, help_text="ht:b")
    d = vodka.config.Attribute(int, default=1, choices=[1,2,3], help_text="ht:d")
    e = vodka.config.Attribute(int, default=1, help_text="ht:e")
    f = vodka.config.Attribute(validator, default=1, help_text="ht:f")
    g = vodka.config.Attribute(int, default=lambda x,i: getattr(i,"default_g"), help_text="ht:g")
    h = vodka.config.Attribute(int, default=1, prepare=[lambda x:x+1])
    
    @classmethod
    def validate_e(self, value):
        return value < 5, "needs to be smaller than 5"

class TestConfig(unittest.TestCase):

    default_g = 2

    def test_prepare(self):
        cfg = {"h" : 1, "b": 1}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(cfg["h"], 2)

    def test_ref(self):
        vodka.config.raw = {
            "a" : {
                "b" : 1
            }
        }

        config = {
            "a" : 0,
            "b" : "@a.b",
            "c" : "@a.b.c",
            "d" : [
                0,
                "@a.b",
                "@a.b.c",
                {
                    "a" : 0,
                    "b" : "@a.b",
                    "c" : "@a.b.c"
                }
            ]
        }

        vodka.config.ref_iter(config)

        self.assertEqual(config, {"a":0,"b":1,"c":None,"d":[0,1,None,{"a":0,"b":1,"c":None}]})
    
    def test_validation(self):
        
        # this should validate without errors
        cfg = {"a" : 1, "b" : 1}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 0)
        self.assertEqual(w, 0)

        # this should return c=2 (2 critical errors) and
        # w=1 (1 warning)
        cfg = {"a": "test", "c":3}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 2)
        self.assertEqual(w, 1)

    def test_check(self):
        
        # this should raise ConfigErrorType
        cfg = {"a" : "invalid type"}
        with self.assertRaises(exc.ConfigErrorType) as inst:
            ConfigHandler.check(cfg, "a", "")

        # this should raise ConfigErrorValue
        cfg = {"d" : 4}
        with self.assertRaises(exc.ConfigErrorValue) as inst:
            ConfigHandler.check(cfg, "d", "")

        # this should raise ConfigErrorUnknown
        cfg = {"c" : 1}
        with self.assertRaises(exc.ConfigErrorUnknown) as inst:
            ConfigHandler.check(cfg, "c", "")

        # this should raise ConfigErrorValue (from custom validation in class method)
        cfg = {"e" : 6}
        with self.assertRaises(exc.ConfigErrorValue) as inst:
            ConfigHandler.check(cfg, "e", "")

        # this should raise ConfigErrorValue (from custom validation in validator)
        cfg = {"f" : 6}
        with self.assertRaises(exc.ConfigErrorValue) as inst:
            ConfigHandler.check(cfg, "f", "")


    def test_default(self):
        
        # default hardset value
        self.assertEqual(ConfigHandler.default("a"), 1)

        # default lambda value with self passed as instance
        self.assertEqual(ConfigHandler.default("g", inst=self), 2)



