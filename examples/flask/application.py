import vodka.app
import vodka.config

@vodka.app.register('my_app')
class MyApp(vodka.app.WebApplication):

    def index(self):
        return self.render("index.html", self.wsgi_plugin.request_env())

    def view(self, id):
        return self.render("view.html", self.wsgi_plugin.request_env())

    def create(self):
        # flask request object
        req = self.wsgi_plugin.request_env().get("request")
