import os
import vodka.log
import vodka.config

class Component(vodka.log.LoggerMixin):
    
    """
    Basic vodka component, all applications and plugins extend
    this class

    Attributes:
        handle (str): unique component handle, override this when extending
    
    Classes:
        Configuration (vodka.config.ComponentHandler): Configuration Handler
    """
    
    handle = "base"

    class Configuration(vodka.config.ComponentHandler):
        pass

    def __init__(self, config):
        self.config = config

    @property
    def home(self):
        """ absolute path to the project home directory """
        return self.get_config('home')

    def get_config(self, key_name):
        """
        Return configuration value 

        Args:
            key_name (str): configuration key

        Returns:
            The value for the specified configuration key, or if not found
            in the config the default value specified in the Configuration Handler
            class specified inside this component

        """
        if key_name in self.config:
            return self.config.get(key_name)
        return self.Configuration.default(key_name, inst=self)

    def resource(self, path):
        """
        Return absolute path to resource

        Args:
            path (str): relative path to resource from project home

        Returns:
            str - absolute path to project resource
        """
        return os.path.join(self.home, path)

