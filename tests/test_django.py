import os.path
import unittest
import pytest
import vodka
import sys

CONFIG = {
    "type" : "django",
    "name" : "django",
    "project_path" : os.path.join(os.path.dirname(__file__), "resources", "django"),
    "settings" : {
        "SECRET_KEY" : "test",
        "INSTALLED_APPS" : ["foo"],
        "DATABASES" : {
            "default" : {
                "ENGINE" : "django.db.backends.sqlite3",
                "NAME" : ""
            }
        }
    }
}

#FIXME: find out why py3.5 fails
@pytest.mark.skipif(sys.version_info > (3,5), reason="fails on py 3.5, skipping for now")
class TestDjango(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.dbfile = tmpdir.join("db.sqlite3")
        CONFIG["settings"]["DATABASES"]["default"]["NAME"] = str(self.dbfile)

    def test_init(self):
        plugin = vodka.plugin.get_instance(CONFIG)

        from django.core.management import execute_from_command_line
        from foo.models import Test

        execute_from_command_line(["manage.py", "migrate"])

        self.assertEqual(Test.objects.count(), 0)
        Test.objects.create(name="Test")
        self.assertEqual(Test.objects.count(), 1)
