import sys
from pluginmgr.config import ConfigPluginManager

from vodka.instance import (
    instances,
    instantiate,
    ready,
    get_instance
)

from vodka.app import (
    load_all,
    applications,
    get_application
)

import vodka.data
import vodka.data.data_types
import vodka.config
import vodka.log

plugin = ConfigPluginManager("vodka.plugins")


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

    # import applications
    load_all(cfg)

    # validating configuration
    vodka.log.debug("making sure configuration is sane ...")
    num_crit, num_warn = vodka.config.InstanceHandler.validate(cfg)
    if num_crit > 0:
        vodka.log.error(
            "There have been %d critical errors detected in the configuration, please fix them and try again" % num_crit)
        sys.exit()

    # instantiate data types
    vodka.log.debug("instantiating data types")
    vodka.data.data_types.instantiate_from_config(cfg.get("data", []))

    # instantiate plugins
    vodka.log.debug("instantiating plugins")
    plugin.instantiate(cfg["plugins"])

    # instantiate vodka applications
    vodka.log.debug("instantiating applications")
    instantiate(cfg)


    vodka.log.debug("starting plugins")

    gevent_workers = []
    thread_workers = []
    asyncio_workers = []

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
        elif async == "thread":
            thread_workers.append(worker)
        elif async == "asyncio":
            asyncio_workers.append(worker)

    ready()

    return {
        "gevent_workers": gevent_workers,
        "thread_workers": thread_workers,
        "asyncio_workers": asyncio_workers
    }


def start(gevent_workers=None, thread_workers=None, asyncio_workers=None):
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

    if gevent_workers:
        import gevent
        _workers = []
        for worker in gevent_workers:
            if isinstance(worker, gevent.Greenlet):
                _workers.append(worker)
            else:
                if hasattr(worker, "run"):
                    _workers.append(gevent.Greenlet(worker.run))
                else:
                    _workers.append(gevent.Greenlet(worker))

        gevent.joinall(_workers)

    if asyncio_workers:
        import asyncio
        import threading
        def run_asyncio():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            for worker in asyncio_workers:
                asyncio.get_event_loop().run_until_complete(worker)
            asyncio.get_event_loop().run_forever()
        t = threading.Thread(target=run_asyncio)
        t.start()


def run(config, rawConfig=None):
    if not rawConfig:
        rawConfig=config
    start(**init(config, rawConfig))
