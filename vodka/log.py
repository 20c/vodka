import logging.config

def log():
    return logging.getLogger("vodka")

def debug(msg):
    return log().debug(msg)

def error(msg):
    return log().error(msg)

def info(msg):
    return log().info(msg)

def warn(msg):
    return log().warn(msg)

def set_loggers(config):
    """
    set loggers up from config
    """

    if not config:
        return

    logging.config.dictConfig(config)


class LoggerMixin(object):
    @property
    def log(self):
        if hasattr(self, "_log"):
            return self._log
        else:
            self._log = logging.getLogger(self.config.get("log", "vodka"))
            return self._log
