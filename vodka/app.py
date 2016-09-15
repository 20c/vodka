"""
Vodka application foundation classes. Each vodka app should extend one
of these.
"""
from builtins import object

import os
import sys
import importlib
import inspect

import pluginmgr

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


def load(name, cfg):

    mod = None

    if not cfg.get("module") and not cfg.get("home"):
        cfg["module"] = "%s.application" % name
    
    if cfg.get("module") and not cfg.get("home"):
        mod = importlib.import_module(cfg.get("module"))
        cfg["home"] = os.path.dirname(inspect.getfile(mod))
    elif cfg.get("home"):
        if cfg.get("home") not in loaded_paths:
            sys.path.append(os.path.split(cfg.get("home").rstrip("/"))[0])
            if cfg.get("module"):
                mod = importlib.import_module(cfg.get("module"))
            else:
                mod = importlib.import_module("%s.application" % name)
            loaded_paths.append(cfg.get("home"))
    else:
        raise KeyError("app config needs to contain 'home' or 'module' key")


def load_all(cfg):
    imported = []

    # load all apps
    for name, app_cfg in list(cfg.get("apps", {}).items()):
        
        # make sure required apps are loaded first
        for req in app_cfg.get("requires", []):
            if req not in imported:
                load(req, cfg["apps"].get(req))
                imported.append(req)
        
        # load the app
        if name not in imported:
            load(name, app_cfg)
            imported.append(name)


# CLASSES

class Application(vodka.component.Component):
    """
    Base application class

    Attributes:
        handle (str): unique handle for the application, override when
            extending
    """

    handle = "base"

    class Configuration(vodka.component.Component.Configuration):
        home = vodka.config.Attribute(
            vodka.config.validators.path,
            default="",
            help_text="absolute path to application directory. you can ignore this if application is to be loaded from an installed python package."
        )
        module = vodka.config.Attribute(
            str,
            default="",
            help_text="name of the python module containing this application (usually <namespace>.application)"
        )

        requires = vodka.config.Attribute(
            list,
            default=[],
            help_text="list of vodka apps required by this app"
        )

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

        template_engine = vodka.config.Attribute(
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
        eng = twentyc.tmpl.get_engine(self.config.get("template_engine", "jinja2"))
        self.tmpl = eng(tmpl_dir=self.template_path)
