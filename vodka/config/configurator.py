import vodka
import vodka.exceptions

class Configurator(object):

    """
    Handles interactive configuration process guided
    by specs defined via config Handler classes
    
    Attributes:
        plugin_manager (PluginManager): plugin manager instance to use
            during plugin configuration
        skip_defaults (bool): if True dont prompt for config variables
            that have a default value assigned
        action_required (list): will hold list of actions required after
            configure call has been completed (if any)
    """

    def __init__(self, plugin_manager, skip_defaults=False):
        self.plugin_manager = plugin_manager
        self.action_required = []
        self.skip_defaults = skip_defaults

    def configure(self, cfg, handler, path=""):
        
        """
        Start configuration process for the provided handler

        Args:
            cfg (dict): config container
            handler (config.Handler class): config handler to use 
            path (str): current path in the configuration progress
        """
        
        # configure simple value attributes (str, int etc.)
        for name, attr in handler.attributes():
            if cfg.get(name) is not None:
                continue
            if not hasattr(attr.expected_type, "__iter__"):
                cfg[name] = self.set(handler, attr, name, path, cfg)
            elif attr.default is None and not hasattr(handler, "configure_%s" % name):
                self.action_required.append(("%s.%s: %s" % (path, name, attr.help_text)).strip("."))
        
        # configure attributes that have complex handlers defined
        # on the config Handler class (class methods prefixed by
        # configure_ prefix
        for name, attr in handler.attributes():
            if cfg.get(name) is not None:
                continue
            if hasattr(handler, "configure_%s" % name):
                fn = getattr(handler, "configure_%s" % name)
                fn(self, cfg, "%s.%s"% (path, name))
                if hasattr(attr.expected_type, "__iter__") and not cfg.get(name):
                    try:
                        del cfg[name]
                    except KeyError:
                        pass


    def set(self, handler, attr, name, path, cfg):
        
        """
        Obtain value for config variable, by prompting the user
        for input and substituting a default value if needed.

        Also does validation on user input
        """

        full_name = ("%s.%s" % (path, name)).strip(".")
        
        # obtain default value
        if attr.default is None:
            default = None
        else:
            try:
                comp = vodka.component.Component(cfg)
                default = handler.default(name, inst=comp)
                if self.skip_defaults:
                    self.echo("%s: %s [default]" % (full_name, default))
                    return default
            except Exception:
                raise

        # render explanation
        self.echo("")
        self.echo(attr.help_text)
        if attr.choices:
            self.echo("choices: %s" % ", ".join([str(c) for c in attr.choices]))
       
        
        # obtain user input and validate until input is valid
        b = False
        while not b:
            try:
                if type(attr.expected_type) == type:
                    r = self.prompt(full_name, default=default, type=attr.expected_type)
                    r = attr.expected_type(r)
                else:
                    r = self.prompt(full_name, default=default, type=str)
            except ValueError:
                self.echo("Value expected to be of type %s"% attr.expected_type)
            try:
                b = handler.check({name:r}, name, path)
            except Exception, inst:
                if hasattr(inst, "explanation"):
                    self.echo(inst.explanation)
                else:
                    raise
        return r
    
    def echo(self, message):
        """ override this function with something that echos a message to the user """
        pass

    def prompt(self, *args, **kwargs):
        """ override this function to prompt for user input """
        return None
 
