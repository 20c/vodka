import unittest
import vodka.data
import vodka.data.handlers
import vodka.data.renderers
import vodka.config
import json

@vodka.data.handlers.register("a")
class HandlerA(vodka.data.handlers.Handler):
    def __call__(self, data, caller=None):
        data["data"][self.handle] = True
        return data

@vodka.data.handlers.register("b")
class HandlerB(vodka.data.handlers.Handler):
    class Configuration(vodka.data.handlers.Handler.Configuration):
        extra = vodka.config.Attribute(int, default=1, help_text="some extra config")
    def __call__(self, data, caller=None):
        data["data"][self.handle] = True
        return data


vodka.data.data_types.instantiate_from_config(
    [{
        "type" : "test",
        "handlers" : [
            {
                "type" : "a"
            },
            {
                "type" : "b",
                "extra" : 123
            }
        ]
    }]
)

class TestData(unittest.TestCase):

    def test_handler_register(self):

        # test that handle a above was registered correctly
        self.assertEqual(vodka.data.handlers.get("a"), HandlerA)
        self.assertEqual(HandlerA.handle, "a")

        # test that handler type 'a' cannot be reused
        with self.assertRaises(KeyError) as inst:
            @vodka.data.handlers.register("a")
            class HandlerA2(HandlerA):
                pass

    def test_handlers_instantiate(self):

        # instantiate single handler
        handler = vodka.data.handlers.instantiate({
            "type" : "a"
        }, "test_a")

        self.assertEqual(handler.__class__, HandlerA)

        # instantiate multiple handlers from data type test
        handlers = vodka.data.handlers.instantiate_for_data_type("test")

        self.assertEqual(len(handlers), 2)
        self.assertEqual(handlers[0].handle, "a")
        self.assertEqual(handlers[1].handle, "b")
        self.assertEqual(handlers[1].get_config("extra"), 123)

    def test_handlers_call(self):
        handlers = vodka.data.handlers.instantiate_for_data_type("test")
        data = {"data" : {"this":"is a test"}}
        expected = {"data" : {"this":"is a test", "a":True, "b":True}}

        for h in handlers:
            data = h(data)

        self.assertEqual(data, expected)


    def test_handle(self):
        data = {"data" : {"this":"is a test"}}
        expected = {"data" : {"this":"is a test", "a":True, "b":True}}
        self.assertEqual(vodka.data.handle("test",data), expected)

    def test_handler_index(self):
        handler = vodka.data.handlers.instantiate({
            "type": "index",
            "index": "name"
        }, "test_b")

        objs = [{"name":"obj %s" % i} for i in range(0,10)]

        data = {"data": objs}
        expected = {"data": dict([(o["name"], o) for o in objs])}
        self.assertEqual(handler(data), expected)

        # test with incomplete data

        objs = [{"name":"obj %s" % i} for i in range(0,10)]
        objs[2] = None
        data = {"data": objs}

        i = 0
        expected = {"data":{}}
        while i < 10:
            if i == 2:
                i+=1
                continue
            o = objs[i]
            expected["data"][o["name"]] = o
            i+=1

        self.assertEqual(handler(data), expected)



    def test_handler_store(self):

        # test list storage

        handler = vodka.data.handlers.instantiate({
            "type": "store",
            "cotainer": "list",
            "limit" : 5
        }, "test_c")

        data = [{"a":i} for i in range(0,10)]

        for d in data:
            handler({"data": d})

        self.assertEqual(len(handler.storage), 5)
        self.assertEqual([{"data":x} for x in data[5:]], handler.storage)

        # test dict storage

        handler = vodka.data.handlers.instantiate({
            "type": "store",
            "container": "dict"
        }, "test_d")

        handler({"data": {"a":1}})
        self.assertEqual(handler.storage, {"a":1})
        handler({"data": {"a":2, "b":1}})
        self.assertEqual(handler.storage, {"a":2, "b":1})




    def test_RPC(self):

        expected_list = {"data":[1,2,3], "meta": {}}
        expected_dict = {"data":{"a":1, "b":2}, "meta": {}}

        # test rpc renderer to json with data type list

        @vodka.data.renderers.RPC(type="json", data_type=list)
        def output_list_json(data,  *args, **kwargs):
            data.extend(expected_list.get("data"))

        self.assertEqual(json.loads(output_list_json()), expected_list)

        # test rpc renderer to json with data type dict

        @vodka.data.renderers.RPC(type="json", data_type=dict)
        def output_dict_json(data,  *args, **kwargs):
            data.update(expected_dict.get("data"))

        self.assertEqual(json.loads(output_dict_json()), expected_dict)

        # test rpc renderer with error catching

        @vodka.data.renderers.RPC(errors=True)
        def output_error(data, *args, **kwargs):
            raise Exception("an error occured")

        self.assertEqual(json.loads(output_error()),
            {
                "data" : [],
                "meta" : {
                    "error" : "an error occured"
                }
            }
        )

        # test rpc renderer on class method
        class Test(object):

            @vodka.data.renderers.RPC(type="json", data_type=list)
            def output(self, data, *args, **kwargs):
                 data.extend(expected_list.get("data"))

        t = Test()
        self.assertEqual(json.loads(t.output()), expected_list)


