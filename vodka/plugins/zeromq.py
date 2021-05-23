try:
    import zmq
except ImportError:
    pass

import vodka
import vodka.plugins
import vodka.config

import traceback


@vodka.plugin.register("zeromq_probe")
class ZeroMQ(vodka.plugins.DataPlugin):
    class Configuration(vodka.plugins.TimedPlugin.Configuration):
        data = vodka.config.Attribute(
            str,
            default="generic",
            help_text="arbitrary descriptor of data retrieved by this zmq probe",
        )

        data_id = vodka.config.Attribute(str, default="")

        bind = vodka.config.Attribute(
            str,
            help_text="bind to this address. In the format of a URL (protocol://host:port)",
        )

    def init(self):
        super().init()
        self.connect()

    def connect(self):
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        try:
            self.sock.setsockopt_string(zmq.SUBSCRIBE, "")
        except TypeError:
            self.sock.setsockopt(zmq.SUBSCRIBE, "")
        self.sock.connect(self.pluginmgr_config.get("bind"))
        return self.ctx, self.sock

    def work(self):
        try:
            return super().work(self.sock.recv_json())
        except zmq.error.ZMQError:
            self.connect()
            self.log.error(traceback.format_exc())
        except Exception:
            self.log.error(traceback.format_exc())
