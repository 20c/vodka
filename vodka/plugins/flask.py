from __future__ import absolute_import
import os
import vodka.plugins.wsgi
import vodka

try:
    from flask import Flask, request, send_from_directory
except ImportError:
    Flask = None

@vodka.plugin.register('flask')
class VodkaFlask(vodka.plugins.wsgi.WSGIPlugin):

    def init(self):
        
        if not Flask:
            raise Exception("Flask could not be imported, make sure flask module is installed")

        # flask app
        flask_app = Flask(
            "__main__"
        )

        flask_app.debug = self.get_config("debug")
        flask_app.use_reloader = False
        self.set_server(flask_app, fnc_serve=flask_app.run)

    def request_env(self, req=None, **kwargs):
        return super(VodkaFlask, self).request_env(req=request, **kwargs)

    def set_static_routes(self):
        def static_file(app, path):
            app = vodka.get_instance(app)
            return send_from_directory(app.get_config('home'), os.path.join("static",path))
        self.set_route(os.path.join(self.get_config('static_url_path'),"<app>","<path:path>"), static_file)

    def set_route(self, path, target, methods=None):
        if not methods:
            methods = ["GET"]
        self.wsgi_application.add_url_rule(
            '%s/' % path, view_func=target, methods=methods)

    def run(self):
        self.wsgi_application.run(self.get_config(
            "host"), self.get_config("port"), use_reloader=False)
