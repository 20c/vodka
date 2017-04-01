import unittest
import uuid
import json
import vodka.log
import vodka.config
import vodka.config.shared as shared
import vodka.exceptions as exc

vodka.log.set_loggers(vodka.log.default_config())


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

class SharedConfigSubHandler(shared.RoutersHandler):
    first = vodka.config.Attribute(str, default="")
    second = vodka.config.Attribute(str, default="")
    third = vodka.config.Attribute(str, default="")
    sub = vodka.config.Attribute(int)

class SharedConfigHandler(vodka.config.Handler):
    a = shared.Attribute(
        dict,
        share="a:merge"
    )
    b = shared.Attribute(
        list,
        share="b:merge"
    )
    c = shared.Attribute(
        list,
        share="c:append"
    )

    d = shared.Container(
        dict,
        share="d:merge",
        handler=lambda x,u: shared.Routers(dict, "d:merge", handler=SharedConfigSubHandler)
    )

    e = shared.Container(
        dict,
        nested=1,
        share="e:merge",
        default={
            "group_1": {"sub_1": {"sub":1, "first":"hello"}}
        },
        handler=lambda x,u: shared.Routers(dict, "e:merge", handler=SharedConfigSubHandler)
    )

    f = shared.Container(
        dict,
        nested=1,
        share="e:merge",
        default={
            "group_1": {"sub_2": {"sub":2, "first":"world"}}
        },
        handler=lambda x,u: shared.Routers(dict, "e:merge", handler=SharedConfigSubHandler)
    )







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


    def test_shared_config(self):

        def uniq():
            return str(uuid.uuid4())

        cfg_a = {"__cfg_a":"a"}
        cfg_b = {"__cfg_b":"b"}

        i = uniq()
        i2 = uniq()
        i3 = uniq()

        for k in ["a"]:
            cfg_a[k] = {"first": i, "second": i2}
            cfg_b[k] = {"third": i2, "second": i}
        for k in ["b", "c"]:
            cfg_a[k] = [i, i2]
            cfg_b[k] = [i, i2]

        cfg_a["d"] = {
            "sub_1" : {"first": i, "second":i2, "sub":1},
            "sub_2" : {"first": i, "second":i2, "sub":2}
        }
        cfg_b["d"] = {
            "sub_1" : {"third": i, "second":i2, "sub":1},
            "sub_2" : {"first": i2, "second":i, "sub":2}
        }
        cfg_b["e"] = {
            "group_1" : { "sub_3": {"first":"sup", "sub":3}},
            "group_2" : { "sub_1": {"first":"well", "sub":1}}
        }

        SharedConfigHandler.validate(cfg_a)
        SharedConfigHandler.validate(cfg_b)

        # test shared dict (merge)
        self.assertEqual(cfg_a["a"], cfg_b["a"])
        self.assertEqual(cfg_a["a"]["third"], i2)
        self.assertEqual(cfg_a["a"]["second"], i)
        self.assertEqual(cfg_a["a"]["first"], i)

        # test shared list (merge)
        self.assertEqual(cfg_a["b"], cfg_b["b"])
        self.assertEqual(cfg_a["b"], [i, i2])

        # test shared list (append)
        self.assertEqual(cfg_a["c"], cfg_b["c"])
        self.assertEqual(cfg_a["c"], [i, i2, i, i2])

        print(cfg_b["e"].keys())
        print(json.dumps(cfg_a["e"], indent=2))


        # test shared dicts in handler (merge)
        self.assertEqual(cfg_a["d"], cfg_b["d"])
        self.assertEqual(cfg_a["d"], {
            "sub_1" : {"first":i, "second": i2, "third": i, "sub": 1},
            "sub_2" : {"first":i2, "second": i, "sub": 2}
        })

        # make sure that default configs got shared as well
        self.assertEqual(cfg_a["e"], {
            "group_1" : {
                "sub_1" : {"first": "hello", "sub":1},
                "sub_2" : {"first": "world", "sub":2},
                "sub_3" : {"first": "sup", "sub":3}
            },
            "group_2" : {
                "sub_1" : {"first":"well", "sub":1}
            }
        })





