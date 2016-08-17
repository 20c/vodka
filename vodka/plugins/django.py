from __future__ import absolute_import

import os
import sys

import vodka
import vodka.config


@vodka.plugin.register('django')
class DjangoPlugin(vodka.plugins.PluginBase): 

    """
    This plugin allows you to use the django ORM in your
    vodka application

    Supports django >= 1.8.14
    """

    class Configuration(vodka.plugins.PluginBase.Configuration):
        
        project_path = vodka.config.Attribute(
            vodka.config.validators.path,
            help_text="absolute path to your django project root"
        )

        settings = vodka.config.Attribute(
            dict,
            default={},
            help_text="django settings object - use uppercase keys as you would inside the actual django settings.py file. Needs INSTALLED_APPS, DATABASES and SECRET_KEY at minimum to function. If omitted, settings located within the django project will be used."
        )


    def init(self):
        p_path = self.get_config("project_path")

        self.log.debug("initializing django from project: %s" % p_path)

        # manually configure settings
        if self.get_config("settings"):
            # settings from vodka config
            from django.conf import settings
            settings.configure(**self.get_config("settings"))
        else:
            # settings from django project
            for f in os.listdir(p_path):
                if os.path.exists(os.path.join(p_path, f, "settings.py")):
                    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % f)
                    break
                
        # so we can import the apps from the django project
        sys.path.append(self.get_config("project_path"))
        
        # need this to start the django apps
        from django.core.wsgi import get_wsgi_application
        self.django_application = get_wsgi_application()
