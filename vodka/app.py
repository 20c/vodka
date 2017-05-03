"""
Vodka application foundation classes. Each vodka app should extend one
of these.
"""
from builtins import object

import os
import sys
import re
import copy
import importlib
import inspect

import pluginmgr

import vodka.config
import vodka.config.shared
import vodka.log
import vodka.component
import vodka.util
import vodka.instance

applications = {}
loaded_paths = []

# FUNCTIONS

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

# DECORATORS

class register(vodka.util.register):
    class Meta(object):
        name = "application"
        objects = applications


# CLASSES

class Application(vodka.component.Component):
    """
    Base application class

    Attributes:
        handle (str): unique handle for the application, override when
            extending
    """

    handle = "base"
    version = None

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


    @classmethod
    def versioned_handle(cls):
        if cls.version is None:
            return cls.handle
        return "%s/%s" %  (cls.handle, cls.version)


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


class SharedIncludesConfigHandler(vodka.config.shared.RoutersHandler):
    path = vodka.config.Attribute(
        str,
        help_text="relative path (to the app's static directory) of the file to be included"
    )

    order = vodka.config.Attribute(
        int,
        default=0,
        help_text="loading order, higher numbers will be loaded after lower numbers"
    )

class TemplatedApplication(Application):
    """
    Application wrapper for an application that is using templates
    to build it's output
    """

    class Configuration(Application.Configuration):
        templates = vodka.config.Attribute(
            vodka.config.validators.path,
            default=lambda k,i: i.resource(k),
            help_text="location of your template files"
        )

        template_locations = vodka.config.Attribute(
            list,
            default=[],
            help_text="allows you to specify additional paths to load templates from"
        )

        template_engine = vodka.config.Attribute(
            str,
            default="jinja2",
            choices=["jinja2"],
            help_text="template engine to use to render your templates"
        )

    @property
    def template_path(self):
        """ absolute path to template directory """
        return self.get_config("templates")


    def versioned_url(self, path):
        #FIXME: needs a more bulletproof solution so it works with paths
        #that already have query parameters attached etc.
        if self.version is None:
            return path
        if not re.match("^%s/.*" % self.handle, path):
            return path
        return "%s?v=%s" % (path, self.version)


    def versioned_path(self, path):
        return re.sub("^%s/" % self.handle, "%s/"%self.versioned_handle(), path)



    def render(self, tmpl_name, context_env):
        """
        Render the specified template and return the output.

        Args:
            tmpl_name (str): file name of the template
            context_env (dict): context environment


        Returns:
            str - the rendered template
        """
        return self.tmpl._render(tmpl_name, context_env)

    def setup(self):
        import twentyc.tmpl

        # set up the template engine
        eng = twentyc.tmpl.get_engine(self.config.get("template_engine", "jinja2"))

        template_locations = []

        # we want tp searcj additional template location specified 
        # in this app's config
        for path in self.get_config("template_locations"):
            if os.path.exists(path):
                self.log.debug("Template location added for application '%s': %s" % (self.handle, path))
                template_locations.append(path)

        # we want to search for template overrides in other app instances
        # that provide templates, by checking if they have a subdir in
        # their template directory that matches this app's handle
        for name, inst in vodka.instance.instances.items():
            if inst == self:
                continue
            if hasattr(inst, "template_path"):
                path = os.path.join(inst.template_path, self.handle)
                if os.path.exists(path):
                    self.log.debug("Template location added for application '%s' via application '%s': %s" % (self.handle, inst.handle, path))
                    template_locations.append(path)

        # finally we add this apps template path to the template locations
        template_locations.append(self.template_path)

        self.tmpl = eng(search_path=template_locations)


class WebApplication(TemplatedApplication):
    """
    Application wrapper for serving content via a web server.
    """

    # Configuration handler

    class Configuration(TemplatedApplication.Configuration):

        includes = vodka.config.shared.Container(
            dict,
            default={},
            nested=1,
            share="includes:merge",
            handler=lambda x,y: vodka.config.shared.Routers(dict, "includes:merge", handler=SharedIncludesConfigHandler),
            help_text="allows you to specify extra media includes for js,css etc."
        )

    # class methods and properties

    @property
    def includes(self):
        """ return includes from config """
        r = dict([(k, sorted(copy.deepcopy(v).values(), key=lambda x:x.get("order",0))) for k,v in self.get_config("includes").items()])
        if self.version is not None:
            for k,v in r.items():
                for j in v:
                    j["path"] = self.versioned_url(j["path"])
        return r


    def render(self, tmpl_name, request_env):
        """
        Render the specified template and return the output.

        Args:
            tmpl_name (str): file name of the template
            request_env (dict): request environment


        Returns:
            str - the rendered template
        """
        return super(WebApplication, self).render(tmpl_name, request_env)


