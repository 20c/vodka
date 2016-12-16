import unittest
import vodka.config.validators

class TestConfigValidators(unittest.TestCase):

    def test_path_validator(self):
        b,d = vodka.config.validators.path(__file__)
        self.assertEqual(b, True)

    def test_host_validator(self):
        b,d = vodka.config.validators.host("host:1")
        self.assertEqual(b, True)

        b,d = vodka.config.validators.host("host")
        self.assertEqual(b, False)

        b,d = vodka.config.validators.host("host:b")
        self.assertEqual(b, False)
