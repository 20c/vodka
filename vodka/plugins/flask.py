from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from past.builtins import basestring
import os
import vodka.plugins.wsgi
import vodka
import vodka.log
import urllib.parse

from functools import update_wrapper


try:
    from flask import (
        Flask,
        request,
        send_from_directory,
        make_response,
        current_app
    )
except ImportError:
    Flask = None

@vodka.plugin.register('flask')
class VodkaFlask(vodka.plugins.wsgi.WSGIPlugin):

    @classmethod
    def decorate_route_crossdomain(cls, origin=None, methods=None, headers=None):

        """
        route decorator that allows for configuration of access control allow
        headers

        Keyword arguments:

            - origin (str, list): allowed origin hosts
            - methods (str, list): allowed origin methods
            - headers (str, list): allowed origin headers

        Example config:

            routes:
              /page:
                target: my_app->target
                crossdomain:
                  origin: '*'
        """

        if methods is not None and not isinstance(methods, basestring):
            methods = ', '.join(sorted(x.upper() for x in methods))
        if headers is not None and not isinstance(headers, basestring):
            headers = ', '.join(x.upper() for x in headers)
        if not isinstance(origin, basestring):
            origin = ', '.join(origin)


        def get_methods():
            if methods is not None:
                return methods
            options_resp = current_app.make_default_options_response()
            return options_resp.headers['allow']

        def decorator(f):
            def wrapped_function(*args, **kwargs):
                if request.method == 'OPTIONS':
                    resp = current_app.make_default_options_response()
                else:
                    resp = make_response(f(*args, **kwargs))
                h = resp.headers
                h['Access-Control-Allow-Origin'] = origin
                h['Access-Control-Allow-Methods'] = get_methods()
                if headers is not None:
                    h['Access-Control-Allow-Headers'] = headers
                return resp

            return update_wrapper(wrapped_function, f)
        return decorator

    def init(self):

        super(VodkaFlask, self).init()

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
        url=urllib.parse.urlparse(request.url)
        return super(VodkaFlask, self).request_env(
            req=request,
            url=url,
            **kwargs
        )


    def set_static_routes(self):
        def static_file(app, path):
            app = vodka.get_instance(app)
            return send_from_directory(app.get_config('home'), os.path.join("static",path))
        self.set_route(os.path.join(self.get_config('static_url_path'),"<app>","<path:path>"), static_file)

        for _url, _path in self.get_config("static_routes").items():
            self.set_route(
                os.path.join(self.get_config("static_url_path"), _url, "<path:path>"),
                lambda path: send_from_directory(_path, path)
            )

    def set_route(self, path, target, methods=None):
        if not methods:
            methods = ["GET"]
        self.wsgi_application.add_url_rule(
            '%s/' % path, view_func=target, methods=methods)

    def run(self):

        ssl_config = self.get_config("ssl")
        if ssl_config.get("enabled"):
            ssl_context = (ssl_config.get("cert"), ssl_config.get("key"))
        else:
            ssl_context = None

        self.wsgi_application.run(
            self.host,
            self.port,
            use_reloader=False,
            ssl_context=ssl_context
        )

