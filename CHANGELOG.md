
# vodka Change Log

## [Unreleased]

### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security

## 2.0.5

### Added
- wsgi: support for route decorators in config
- wsgi: added 'host' variable to template env 
- flask: crossdomain route decorator

## 2.0.4

### Added
- documentation
- application configuration attribute: requires - allows an application to specify other applications as required to make sure they get loaded first in the app loading process
- gunicorn wsgi server support
- web application ssl support

### Fixed
- module name specified in application config is now always respected
- newapp command will now create an __init__.py file
- applications can now provide their own plugins
- gevent async handler

### Removed
- util.SearchPathImporter as it was redundant

## 2.0.3

### Added
- bartender command: 'newapp', generates a blank vodka application stucture
- util.SearchPathImporter for vodka application loading

### Changed
- refactored app loading to allow each app to have a separate home location
  which also makes it now possible to load multiple apps from multiple 
  sources
- wsgi plugin: request env now contains an app object for each instantiated app 
  with a static_url member to allow loading of app specific static resources

### Deprecated
- home config variable in vodka config root, replaced by app home

## 2.0.2 

### Added
- plugins/django, allows you to use django's orm 
- bartender command: 'config', interactive config creation
- impl plugin.setup() method that is called right before a plugin is started
- impl base class for class registry decorator
- additional unittests 

### Fixed
- plugins/flask, fail gracefully when trying to import flask

### Changed
- plugins are now instantiated before applications
- vodka.app.register now a decorator
