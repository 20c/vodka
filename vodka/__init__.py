import sys
from pluginmgr import PluginManager

from vodka.instance import (
    instances,
    instantiate,
    ready,
    get_instance
)

from vodka.app import (
    load,
    applications,
    get_application
)

import vodka.data
import vodka.config
import vodka.log

plugin = PluginManager("vodka.plugins")


def init(config, rawConfig):

    # reference the complete config in vodka.config.raw
    if type(rawConfig) in [dict, vodka.config.Config]:
        vodka.config.raw.update(**rawConfig)
    else:
        vodka.config.raw.update(**rawConfig.data)

    # reference the vodka instance config in vodka.config.instance
    if type(config) in [dict, vodka.config.Config]:
        cfg = config
        vodka.config.instance.update(**cfg)
    else:
        cfg = vodka.config.Config(read=config)
        vodka.config.instance.update(**cfg.data)

    # set up loggers
    vodka.log.set_loggers(cfg.get("logging", {}))

    if "home" not in cfg:
        raise KeyError(
            "Need to specify vodka application home in config 'home' variable")

    vodka.config.instance["home"] = cfg[
        "home"] = vodka.config.prepare_home_path(cfg["home"])

    # instantiate data types
    vodka.log.debug("instantiating data types")
    vodka.data.data_types.instantiate_from_config(cfg.get("data", []))

    # instantiate plugins
    vodka.log.debug("instantiating plugins")
    plugin.instantiate(cfg["plugins"])

    # import main application
    app_home = cfg.get("home")
    vodka.log.debug("importing app from: %s" % app_home)
    load(app_home)

    # instantiate vodka applications
    vodka.log.debug("instantiating applications")
    instantiate(cfg)


    vodka.log.debug("making sure configuration is sane ...")

    num_crit, num_warn = vodka.config.InstanceHandler.validate(cfg)

    if num_crit > 0:
        vodka.log.error(
            "There have been %d critical errors detected in the configuration, please fix them and try again" % num_crit)
        sys.exit()

    vodka.log.debug("starting plugins")

    gevent_workers = []
    thread_workers = []

    for pcfg in cfg["plugins"]:
        p_name = pcfg.get("name", pcfg.get("type"))
        p = plugin.get_instance(p_name)
        
        p.setup()

        if pcfg.get("start_manual", False):
            continue
        vodka.log.debug("starting %s .." % p_name)
        async = pcfg.get("async", "thread")

        if hasattr(p, "worker"):
            worker = p.worker
        else:
            worker = p

        if async == "gevent":
            gevent_workers.append(worker)
            worker.start()
        elif async == "thread":
            thread_workers.append(worker)

    ready()

    return {
        "gevent_workers": gevent_workers,
        "thread_workers": thread_workers
    }


def start(gevent_workers=None, thread_workers=None):
    if gevent_workers:
        import gevent
        gevent.joinall(gevent_workers)
    if thread_workers:
        import threading
        for w in thread_workers:
            if hasattr(w, "start"):
                t = threading.Thread(target=w.start)
            else:
                t = threading.Thread(target=w)
            # FIXME: need plugin shutdown instead
            t.daemon = True
            t.start()


def run(config, rawConfig):
    start(**init(config, rawConfig))
