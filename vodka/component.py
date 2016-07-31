import os
import vodka.log
import vodka.config

class Component(vodka.log.LoggerMixin):
    
    handle = "base"

    class Configuration(vodka.config.ComponentHandler):
        pass

    @property
    def home(self):
        return vodka.config.instance.get("home")

    def get_config(self, key_name):
        return self.config.get(key_name, self.Configuration.default(key_name, inst=self))

    def config_ref(self, value):
        return vodka.config.ref(value)

    def resource(self, path):
        return os.path.join(self.home, path)

