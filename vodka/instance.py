from vodka.app import get_application 

instances = {}

def get_instance(name):
    """
    wrapper function to retrieve instance

    Args:
        name (str): instance name - identical to appliction class handle value

    Returns:
        application instance with the matching name

    Raises:
        KeyError: No instance found for specified name
    """

    if name in instances:
        return instances.get(name)
    raise KeyError("No instance spawned for application handle '%s'" % name)

def instantiate(config):

    """
    instantiate all registered vodka applications

    Args:
        config (dict or MungeConfig): configuration object
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
