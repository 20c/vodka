
# vodka Change Log

## [Unreleased]

### Added
- bartender command: 'newapp', generates a blank vodka application stucture
- util.SearchPathImporter for vodka application loading

### Fixed

### Changed
- refactored app loading to allow each app to have a separate home location
  which also makes it now possible to load multiple apps from multiple 
  sources
- wsgi plugin: request env now contains an app object for each instantiated app 
  with a static_url member to allow loading of app specific static resources

### Deprecated
- home config variable in vodka config root, replaced by app home

### Removed

### Security

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

### Deprecated

### Removed

### Security
