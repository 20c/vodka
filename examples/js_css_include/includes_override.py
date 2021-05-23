@vodka.app.register('test_app')
class TestApp(vodka.app.WebApplication):
    # configuration

    class Configuration(vodka.app.WebApplication.Configuration):

        includes = vodka.config.Attribute(
            dict,
            default={
                "js" : {
                    "jquery" : {"path":"test_app/js/jquery.js"},
                },
                "css": {
                    "bootstrap" : {"path":"test_app/media/bootstrap.css"},
                }
            },
            handler=lambda x,y: vodka.config.shared.Routers(dict, "includes:merge", handler=SharedIncludesConfigHandler),
            help_text="allows you to specify extra media includes for js,css etc."
        )
