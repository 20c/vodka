Create a file called uwsgi_app.py in your vodka application directory

    import os
    import vodka

    from vodka.plugins.wsgi import WSGIPlugin

    vodka.run(
        ".",
        os.environ.get("VODKA_HOME", ".")
    )
    
    application = WSGIPlugin.wsgi_application

Then run uwsgi against it

    uwsgi -H $VIRTUAL_ENV --socket=0.0.0.0:8021 -w uwsgi_app:application --enable-threads
