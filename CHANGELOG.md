
# vodka Change Log

## [Unreleased]

### Added
- bartender command: 'newapp', generates a blank vodka application stucture

### Fixed

### Changed

### Deprecated

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
