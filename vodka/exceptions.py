class ConfigErrorMixin(object):

    handle = "config error"
   
    def __init__(self, value=None, attr=None, level="warn", reason=None):
        self.attr = attr
        self.value = value
        self.level = level
        self.reason = reason

    @property
    def help_text(self):
        if self.attr:
            return self.attr.help_text
        return ""

    @property
    def explanation(self):
        r = "[%s] %s" % (self.handle, str(self))
        if self.reason:
            r = "%s, reason: %s" % (r, self.reason)
        if self.attr:
            r = "%s -> %s" % (r, self.help_text)
            if self.attr.choices:
                r = "%s (choices=%s)" % (r, ",".join(self.attr.choices))

        return r


class ConfigErrorValue(ConfigErrorMixin, ValueError):
    
    """
    This configuration error is raised when a config variable
    has an invalid value. Note that this is separate from a type
    mismatch error which will raise ConfigErrorType
    """

    handle = "config value invalid"

    def __init__(self, var_name, attr, value, reason=None, level="critical"):
        
        ValueError.__init__(
            self,
            "%s contains an invalid value" % var_name
        )
        ConfigErrorMixin.__init__(self, attr=attr, value=value, level=level, reason=reason)

class ConfigErrorMissing(ConfigErrorMixin, KeyError):
    
    """
    This configuration error is raised when a required config variable
    is missing
    """

    handle = "config missing"

    def __init__(self, var_name, attr, level="critical"):
        KeyError.__init__(
            self,
            "%s is missing from config file" % var_name
        )
        ConfigErrorMixin.__init__(self, attr=attr, level=level)

class ConfigErrorType(ConfigErrorMixin, TypeError):
    
    """
    This configuration error is raised when a config variable is 
    missconfigured with an invalid type for its value
    """

    handle = "config type mismatch"

    def __init__(self, var_name, attr, level="critical"):
        TypeError.__init__(
            self,
            "%s should be of type '%s'" % (var_name, attr.expected_type.__name__)
        )
        ConfigErrorMixin.__init__(self, attr=attr, level=level)


class ConfigErrorUnknown(ConfigErrorMixin, KeyError):
    
    """
    This configuration error is raised when a config variable is
    specified but unknown to vodka
    """

    handle = "config unknown"

    def __init__(self, var_name, level="warn", attr=None):
        KeyError.__init__(
            self,
            "%s is not a known configuration variable and has been ignored" % var_name
        )
        ConfigErrorMixin.__init__(self, attr=None, level=level)
