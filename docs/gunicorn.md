Create a file called wsgi_app.py in your vodka application directory

    import os
    import vodka
    import vodka.config

    from vodka.plugins.wsgi import WSGIPlugin

    config = vodka.config.Config()
    config.read(config_dir=os.environ.get("VODKA_HOME", "."))

    vodka.run(config)

    application = WSGIPlugin.wsgi_application


Then run uwsgi against it

    gunicorn -b 0.0.0.0:7026 wsgi_app:application
