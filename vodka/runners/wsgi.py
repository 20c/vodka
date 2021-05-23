import os
import vodka
import vodka.config

import vodka.load_entrypoints

from vodka.plugins.wsgi import WSGIPlugin


config = vodka.config.Config()
config.read(config_dir=os.environ.get("VODKA_HOME", "."))

vodka.run(config, config)

application = WSGIPlugin.wsgi_application
