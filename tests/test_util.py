import unittest
import vodka.util

class TestUtil(unittest.TestCase):

    def test_dict_get_path(self):
        a = {"1":{"2":{"3":"end"}}}
        b = {"1":[{"x":"end","name":"a"},{"c":{"x":"end"},"name":"b"}]}
        self.assertEqual(vodka.util.dict_get_path(a,"1.2.3"), "end")
        self.assertEqual(vodka.util.dict_get_path(a,"a.b.c"), None)
        self.assertEqual(vodka.util.dict_get_path(a,"a.b.c", default="end"), "end")

        self.assertEqual(vodka.util.dict_get_path(b,"1.a.x"), "end")
        self.assertEqual(vodka.util.dict_get_path(b,"1.b.c.x"), "end")
        self.assertEqual(vodka.util.dict_get_path(b,"1.c.x"), None)
