# Web Application

```yml
{!examples/flask/application.py!}
```

# WSGI Frameworks

## Flask

Currently the only supported wsgi framework is flask, although we hope to extend this soon.

### Install requirements

```sh
pip install flask
```

### Plugin configuration

```yml
{!examples/flask/config.yml!}
```

# WSGI Servers

Can be specified by setting the 'server' config attribute in your wsgi framework config (eg. flask plugin config)

## Gevent

- config value: 'gevent'

### Install requirements

```sh
pip install gevent
```

### Run

```sh
bartender serve --config=/path/to/vodka/home
```

## Gunicorn

- config value: 'gunicorn'

### Install requirements

```sh
pip install gunicorn
```

### Run

```sh
export VODKA_HOME=/path/to/vodka/home
gunicorn -b 0.0.0.0:7026 vodka.runners.wsgi:application
```

## UWSGI

- config value: 'uwsgi'

### Install requirements

```sh
pip install uwsgi 
```

### Run

```sh
export VODKA_HOME=/path/to/vodka/home
uwsgi -H $VIRTUAL_ENV --socket=0.0.0.0:7026 -w vodka.runners.wsgi:application --enable-threads
```


