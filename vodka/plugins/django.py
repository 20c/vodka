from __future__ import absolute_import

import sys

import vodka
import vodka.config


@vodka.plugin.register('django')
class DjangoPlugin(vodka.plugins.PluginBase): 

    """
    This plugin allows you to use the django ORM in your
    vodka application
    """

    class Configuration(vodka.plugins.PluginBase.Configuration):
        
        project_path = vodka.config.Attribute(
            vodka.config.validators.path,
            help_text="absolute path to your django project root"
        )

        settings = vodka.config.Attribute(
            dict,
            help_text="django settings object - use uppercase keys as you would inside the actual django settings.py file. Needs INSTALLED_APPS, DATABASES and SECRET_KEY at minimum to function."
        )


    def init(self):
        # manually configure settings
        from django.conf import settings
        settings.configure(**self.get_config("settings"))

        # so we can import the apps from the django project
        sys.path.append(self.get_config("project_path"))
        
        # need this to start the django apps
        from django.core.wsgi import get_wsgi_application
        self.django_application = get_wsgi_application()
