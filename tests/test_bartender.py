import unittest
import pytest
import json
import os

import vodka.config
import vodka.log
import vodka.bartender
import vodka.plugins
import vodka.app
import vodka

from click.testing import CliRunner

HOME =  os.path.join(os.path.dirname(__file__), "resources", "bartender")

@vodka.plugin.register('test_bartender_a')
class Plugin(vodka.plugins.PluginBase):
    pass

class SimPromptConfigurator(vodka.bartender.ClickConfigurator):

    """
    We make a configurator that simulates user input for
    the bartender config test. values will be sent to prompts
    in order
    """
    
    values = [
        # home
        HOME,
        # add plugin type
        "test_bartender_a",
        # dont add another plugin
        "skip"
    ]
    
    def prompt(self, msg, default=None, *args, **kwargs):
        if not hasattr(self, "counter"):
            self.counter = 0
        
        # default value is provided, use that
        if default and default != "skip":
            return default
        
        r = self.values[self.counter]
        self.counter += 1
        return r
# override so config cli will use our new sim prompt configurator
vodka.bartender.ClickConfigurator = SimPromptConfigurator


class TestBartender(unittest.TestCase):

    """
    Tests bartender CLI
    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.config_file = tmpdir.join("config.json")
        self.cli = CliRunner()

    def test_check_config(self):
        """
        Test the check_config command
        """

        # create config to check, this should always validate
        self.config_file.write(json.dumps({
            "logging" : vodka.log.default_config(),
            "home" : HOME
        }))
        
        # run check_config
        r = self.cli.invoke(vodka.bartender.check_config, ["--config=%s" % str(self.tmpdir)])

        # assert no errors
        self.assertEqual(r.exit_code, 0)

        # assert output
        self.assertEqual(str(r.output), "Checking config at %s for errors ...\n0 config ERRORS, 0 config WARNINGS\n" % str(self.tmpdir))
        
    
    def test_config(self):
        
        """
        Test the config command

        This will will generate a config based on user input and default values
        """

        # run config (this will use SimPrompt
        r = self.cli.invoke(vodka.bartender.config, ["--config=%s/config.json" % str(self.tmpdir)])

        # assert no errors
        self.assertEqual(r.exit_code, 0)

        cfg = vodka.config.Config(read=str(self.tmpdir))
        print cfg.data
        expected = {
            'home': HOME, 
            'apps': {
                'test_bartender_app': {'enabled': True}
            }, 
            'plugins': [
                {
                    'async': 'thread', 
                    'enabled': True, 
                    'name': 'test_bartender_a', 
                    'type': 'test_bartender_a'
                }
            ]
        }
        self.assertEqual("home" in cfg.data, True)
        self.assertEqual("apps" in cfg.data, True)
        self.assertEqual("plugins" in cfg.data, True)
        self.assertEqual(expected["home"], cfg.data["home"])
        # note: because other tests may register applications we
        # cannot directly compare the entire content of "apps"
        self.assertEqual(expected["apps"]["test_bartender_app"], cfg.data["apps"]["test_bartender_app"])
        self.assertEqual(expected["plugins"], cfg.data["plugins"])
