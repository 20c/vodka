"""
Vodka application foundation classes. Each vodka app should extend one
of these.
"""

import vodka.config 
import vodka.log
import vodka.component

applications = {}

# FUNCTIONS

def register(cls):
    """
    Register an application
    """

    if cls.handle in applications:
        raise KeyError("Application with handle '%s' already registered" % cls.handle)
    applications[cls.handle] = cls

def get_application(handle):
    """
    Wrapper function to retrieve registered application
    """

    if handle in applications:
        return applications.get(handle)
    raise KeyError("Application with handle '%s' not registered" % handle)

# CLASSES

class Application(vodka.component.Component):
    """
    Base application class
    """

    handle = "base"

    def __init__(self, config=None, config_dir=None):
        if config:
            self.config = config
        elif config_dir:
            self.config = config.Config(read=config_dir)
        else:
            raise ValueError("No configuration specified")

    def setup(self):
        pass



class WebApplication(Application):
    """
    Application targeted at serving content to the web.
    """

    # Configuration handler

    class Configuration(Application.Configuration):

        templates = vodka.config.Attribute(
            vodka.config.validators.path, 
            default=lambda k,i: i.resource(k), 
            help_text="location of your template files"
        )

        tmpl_engine = vodka.config.Attribute(
            str, 
            default="jinja2", 
            choices=["jinja2"], 
            help_text="template engine to use to render your templates"
        )
    
    # class methods and properties

    @property
    def template_path(self):
        return self.get_config("templates")

    def render(self, tmpl_name, request_env):
        return self.tmpl._render(tmpl_name, request_env)

    def setup(self):
        import twentyc.tmpl
        eng = twentyc.tmpl.get_engine(self.config.get("tmpl_engine", "jinja2"))
        self.tmpl = eng(tmpl_dir=self.template_path)
