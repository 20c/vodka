from vodka.app import get_application 

instances = {}

def get_instance(name):
    """
    wrapper function to retrieve instance
    """

    if name in instances:
        return instances.get(name)
    raise KeyError("No instance spawned for application handle '%s'" % name)

def instantiate(config):

    """
    instantiate all registered vodka applications
    """
    
    for handle, cfg in config["apps"].items():
        if not cfg.get("enabled", True):
            continue
        app = get_application(handle)
        instances[app.handle] = app(cfg)

def ready():
    
    """
    Runs setup() method on all instantiated vodka apps
    """
  
    for handle, instance in instances.items():
        instance.setup()
