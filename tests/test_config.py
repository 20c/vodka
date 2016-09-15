import unittest
import vodka.config
import vodka.exceptions as exc


def validator(value):
    return value < 5, "needs to be smaller than 5"

class ListHandler(vodka.config.Handler):
    a = vodka.config.Attribute(int, default=1, help_text="lh:a")
    b = vodka.config.Attribute(int, help_text="lh:b")

class DictHandler(vodka.config.Handler):
    a = vodka.config.Attribute(int, default=1, help_text="dh:a")
    b = vodka.config.Attribute(int, help_text="dh:b")

class DictHandlerProxy(vodka.component.Component):
    class Configuration(vodka.config.Handler):
      a = vodka.config.Attribute(int, default=1, help_text="dh:a")
      b = vodka.config.Attribute(int, help_text="dh:b")

class ConfigHandler(vodka.config.Handler):
    a = vodka.config.Attribute(int, default=1, help_text="ht:a")
    b = vodka.config.Attribute(int, help_text="ht:b")
    d = vodka.config.Attribute(int, default=1, choices=[1,2,3], help_text="ht:d")
    e = vodka.config.Attribute(int, default=1, help_text="ht:e")
    f = vodka.config.Attribute(validator, default=1, help_text="ht:f")
    g = vodka.config.Attribute(int, default=lambda x,i: getattr(i,"default_g"), help_text="ht:g")
    h = vodka.config.Attribute(int, default=1, prepare=[lambda x:x+1])
    i = vodka.config.Attribute(int, default=1)
    j = vodka.config.Attribute(list, default=[], handler=lambda x,y: ListHandler)
    k = vodka.config.Attribute(dict, default={}, handler=lambda x,y: DictHandler)
    l = vodka.config.Attribute(dict, default={}, handler=lambda x,y: DictHandlerProxy)
    depr = vodka.config.Attribute(int, default=1, help_text="ht:depr", deprecated="2.2.0")
    
    @classmethod
    def validate_e(self, value):
        return value < 5, "needs to be smaller than 5"
    
    @classmethod
    def prepare_i(self, value, config=None):
        return value + 1

class TestConfig(unittest.TestCase):

    default_g = 2

    def test_prepare(self):
        cfg = {"h" : 1, "b": 1}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(cfg["h"], 2)

    def test_prepare_via_handler(self):
        cfg = {"i" : 1, "b": 1}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(cfg["i"], 2)

    def test_nested_validation(self):
        
        # should pass validation
        cfg = {"b":1, "j":[{"a":1, "b":1}]}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 0)
        self.assertEqual(w, 0)
        
        # should detect b missing from list element
        cfg = {"b":1, "j":[{"a":1}]}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 1)
        self.assertEqual(w, 0)

        # should detect b missing from dict element
        cfg = {"b":1, "k":{"1":{"a":1}}}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 1)
        self.assertEqual(w, 0)

        # should detect b value mismatch in list element 
        cfg = {"b":1, "j":[{"a":1,"b":"z"}]}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 1)
        self.assertEqual(w, 0)

        # should detect b missing from dict element and a value mismatch
        cfg = {"b":1, "l":{"1":{"a":"z"}}}
        c,w = ConfigHandler.validate(cfg)
        self.assertEqual(c, 2)
        self.assertEqual(w, 0)




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



