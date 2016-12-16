Create a file called uwsgi_app.py in your vodka application directory

    import os
    import vodka
    import vodka.config

    from vodka.plugins.wsgi import WSGIPlugin

    config = vodka.config.Config()
    config.read(config_dir=os.environ.get("VODKA_HOME", "."))

    vodka.run(config, config)

    application = WSGIPlugin.wsgi_application


Then run uwsgi against it

    uwsgi -H $VIRTUAL_ENV --socket=0.0.0.0:8021 -w uwsgi_app:application --enable-threads
