"""
Vodka application foundation classes. Each vodka app should extend one
of these.
"""

import sys
import imp

import vodka.config 
import vodka.log
import vodka.component
import vodka.util

applications = {}
loaded_paths = []

# FUNCTIONS

class register(vodka.util.register):
    class Meta(object):
        name = "application"
        objects = applications

def get_application(handle):
    """
    Wrapper function to retrieve registered application class

    Args:
        handle (str): application handle as defined in the application class

    Returns:
        the application class with the matching handle

    Raises:
        KeyError: Application with specified handle is not registered
    """

    if handle in applications:
        return applications.get(handle)
    raise KeyError("Application with handle '%s' not registered" % handle)

def load(app_home):
    """ 
    load applications located in path specified by app_home 

    Args:
        app_home (str): path to application home directory, expected to
            contain application.py file
    """
    if app_home in loaded_paths:
        return
    imp.load_source("application", "%s/application.py" % app_home)
    loaded_paths.append(app_home)


# CLASSES

class Application(vodka.component.Component):
    """
    Base application class

    Attributes:
        handle (str): unique handle for the application, override when
            extending
    """

    handle = "base"

    def __init__(self, config=None, config_dir=None):
        
        """
        Kwargs:
            config (dict or MungeConfig): configuration object, note that
                either this or config_dir need to be specified.
            config_dir (str): path to config directory, will attempt to
                read into a new MungeConfig instance from there.
        """

        if config:
            self.config = config
        elif config_dir:
            self.config = config.Config(read=config_dir)
        else:
            raise ValueError("No configuration specified")

    def setup(self):
        """
        Soft initialization method with no arguments that can easily be 
        overwritten by extended classes
        """
        pass



class WebApplication(Application):
    """
    Application wrapper for serving content via a web server.
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
        """ absolute path to template directory """
        return self.get_config("templates")

    def render(self, tmpl_name, request_env):
        """
        Render the specified template and return the output.

        Args:
            tmpl_name (str): file name of the template
            request_env (dict): request environment
        

        Returns:
            str - the rendered template 
        """
        return self.tmpl._render(tmpl_name, request_env)

    def setup(self):
        import twentyc.tmpl

        # set up the template engine
        eng = twentyc.tmpl.get_engine(self.config.get("tmpl_engine", "jinja2"))
        self.tmpl = eng(tmpl_dir=self.template_path)
