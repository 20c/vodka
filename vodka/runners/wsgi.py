import os
import vodka
import vodka.config

from vodka.plugins.wsgi import WSGIPlugin

config = vodka.config.Config()
config.read(config_dir=os.environ.get("VODKA_HOME", "."))

vodka.run(config, config)

application = WSGIPlugin.wsgi_application
