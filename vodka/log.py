import logging.config

def default_config(level="DEBUG"):
    return {
        "version" : 1,
        "formatters" : {
            "simple" : {
                "format" : "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
             }
        },
        "handlers" : {
            "console" : {
                "class" : "logging.StreamHandler",
                "level" : level.upper(),
                "formatter" : "simple",
                "stream" : "ext://sys.stdout"
            }
        },
        "loggers" : {
            "vodka" : {
                "level" : level.upper(),
                "handlers" : ["console"]
            }
        }
    }
    
def log():
    """Return the default logger set up for vodka"""
    return logging.getLogger("vodka")

def debug(msg):
    """
    Log debug message using the default logger

    Args:
        msg (str): message
    """
    return log().debug(msg)

def error(msg):
    """
    Log error message using the default logger

    Args:
        msg (str): message
    """
    return log().error(msg)

def info(msg):
    """
    Log info message using the default logger

    Args:
        msg (str): message
    """
    return log().info(msg)

def warn(msg):
    """
    Log warning message using the default logger

    Args:
        msg (str): message
    """
    return log().warn(msg)

def set_loggers(config):
    """
    set loggers up from config
    """

    if not config:
        return

    logging.config.dictConfig(config)


class LoggerMixin(object):
    
    """
    Mixin class that sets a 'log' property that will either return
    the default vodka logger, or a logger specified in the object's
    configuration attribute.

    This mixin expects the class it is attached to have a 'config'
    attribute that is either of type dict or MungeConfig
    """

    @property
    def log(self):
        if hasattr(self, "_log"):
            return self._log
        else:
            self._log = logging.getLogger(self.config.get("log", "vodka"))
            return self._log
