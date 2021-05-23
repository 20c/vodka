import munge
import types
import os
import os.path

import vodka.app
import vodka.exceptions
import vodka.log
import vodka.util

from . import validators

raw = {}

instance = {}


def is_config_container(v):
    """
    checks whether v is of type list,dict or Config
    """

    cls = type(v)

    return issubclass(cls, list) or issubclass(cls, dict) or issubclass(cls, Config)


class Attribute:

    """
    A configuration attribute
    """

    def __init__(self, expected_type, **kwargs):
        """
        Args:
            expected_type (class or function): type expected for this attribute, if specified
                as a function the result of the function will determine whether or not the value
                passed type validation.

        Kwargs:
            default: if specified this value will be used as a default value, if not specified then
                configuration of this attribute is treated as mandatory
            help_text (str): explains the attribute
            choices (list): list of valid value choices for this attribute, if set any value not
                matching any of the choices will raise a configuration error
            handler (function): when the value for this attribute is a collection of configuration
                attributes (e.g. nested config) use this function to return the aproporiate config
                handler class to use to validate them
            prepare (function): allows you to prepare value for this attribute
            deprecated (str): if not None indicates that this attribute is still functional but
                deprecated and will be removed in the vodka version specified in the value
        """

        self.expected_type = expected_type
        self.default = kwargs.get("default")
        self.help_text = kwargs.get("help_text")
        self.handler = kwargs.get("handler")
        self.choices = kwargs.get("choices")
        self.prepare = kwargs.get("prepare", [])
        self.deprecated = kwargs.get("deprecated", False)
        self.nested = kwargs.get("nested", 0)
        self.field = kwargs.get("field")

    def finalize(self, cfg, key_name, value, **kwargs):
        pass

    def preload(self, cfg, key_name, **kwargs):
        pass


class Handler:

    """
    Can be attached to any vodka application class or vodka
    plugin and allows to setup default values and config
    sanity checking
    """

    @classmethod
    def check(cls, cfg, key_name, path, parent_cfg=None):
        """
        Checks that the config values specified in key name is
        sane according to config attributes defined as properties
        on this class
        """

        attr = cls.get_attr_by_name(key_name)

        if path != "":
            attr_full_name = f"{path}.{key_name}"
        else:
            attr_full_name = key_name

        if not attr:
            # attribute specified by key_name is unknown, warn
            raise vodka.exceptions.ConfigErrorUnknown(attr_full_name)

        if attr.deprecated:
            vodka.log.warn(
                "[config deprecated] {} is being deprecated in version {}".format(
                    attr_full_name, attr.deprecated
                )
            )

        # prepare data
        for prepare in attr.prepare:
            cfg[key_name] = prepare(cfg[key_name])

        if hasattr(cls, "prepare_%s" % key_name):
            prepare = getattr(cls, "prepare_%s" % key_name)
            cfg[key_name] = prepare(cfg[key_name], config=cfg)

        value = cfg.get(key_name)

        if isinstance(attr.expected_type, types.FunctionType):
            # expected type holds a validator function
            p, reason = attr.expected_type(value)
            if not p:
                # validator did not pass
                raise vodka.exceptions.ConfigErrorValue(
                    attr_full_name, attr, value, reason=reason
                )

        elif attr.expected_type != type(value):
            # attribute type mismatch
            raise vodka.exceptions.ConfigErrorType(attr_full_name, attr)

        if attr.choices and value not in attr.choices:
            # attribute value not valid according to
            # available choices
            raise vodka.exceptions.ConfigErrorValue(attr_full_name, attr, value)

        if hasattr(cls, "validate_%s" % key_name):
            # custom validator for this attribute was found
            validator = getattr(cls, "validate_%s" % key_name)
            valid, reason = validator(value)
            if not valid:
                # custom validator failed
                raise vodka.exceptions.ConfigErrorValue(
                    attr_full_name, attr, value, reason=reason
                )

        num_crit = 0
        num_warn = 0

        if is_config_container(value) and attr.handler:
            if type(value) == dict or issubclass(type(value), Config):
                keys = list(value.keys())
            elif type(value) == list:
                keys = list(range(0, len(value)))
            else:
                return
            for k in keys:
                if not is_config_container(value[k]):
                    continue
                handler = attr.handler(k, value[k])
                if issubclass(handler, Handler):
                    h = handler
                else:
                    h = getattr(handler, "Configuration", None)

                # h = getattr(attr.handler(k, value[k]), "Configuration", None)
                if h:
                    if (
                        type(k) == int
                        and type(value[k]) == dict
                        and value[k].get("name")
                    ):
                        _path = "{}.{}".format(attr_full_name, value[k].get("name"))
                    else:
                        _path = f"{attr_full_name}.{k}"
                    _num_crit, _num_warn = h.validate(
                        value[k], path=_path, nested=attr.nested, parent_cfg=cfg
                    )
                    h.finalize(
                        value,
                        k,
                        value[k],
                        attr=attr,
                        attr_name=key_name,
                        parent_cfg=cfg,
                    )
                    num_crit += _num_crit
                    num_warn += _num_warn

        attr.finalize(cfg, key_name, value, num_crit=num_crit)

        return (num_crit, num_warn)

    @classmethod
    def finalize(cls, cfg, key_name, value, **kwargs):
        """
        Will be called after validation for a config variable
        is completed
        """
        pass

    @classmethod
    def validate(cls, cfg, path="", nested=0, parent_cfg=None):
        """
        Validates a section of a config dict. Will automatically
        validate child sections as well if their attribute pointers
        are instantiated with a handler property
        """

        # number of critical errors found
        num_crit = 0

        # number of non-critical errors found
        num_warn = 0

        # check for missing keys in the config
        for name in dir(cls):
            if nested > 0:
                break
            try:
                attr = cls.get_attr_by_name(name)
                if isinstance(attr, Attribute):
                    if attr.default is None and name not in cfg:
                        # no default value defined, which means its required
                        # to be set in the config file
                        if path:
                            attr_full_name = f"{path}.{name}"
                        else:
                            attr_full_name = name
                        raise vodka.exceptions.ConfigErrorMissing(attr_full_name, attr)
                    attr.preload(cfg, name)

            except vodka.exceptions.ConfigErrorMissing as inst:
                if inst.level == "warn":
                    vodka.log.warn(inst.explanation)
                    num_warn += 1
                elif inst.level == "critical":
                    vodka.log.error(inst.explanation)
                    num_crit += 1

        if type(cfg) in [dict, Config]:
            keys = list(cfg.keys())
            if nested > 0:
                for _k, _v in list(cfg.items()):
                    _num_crit, _num_warn = cls.validate(
                        _v, path=(f"{path}.{_k}"), nested=nested - 1, parent_cfg=cfg
                    )
                    num_crit += _num_crit
                    num_warn += _num_warn
                return num_crit, num_warn
        elif type(cfg) == list:
            keys = list(range(0, len(cfg)))
        else:
            raise ValueError("Cannot validate non-iterable config value")

        # validate existing keys in the config
        for key in keys:
            try:
                _num_crit, _num_warn = cls.check(cfg, key, path)
                num_crit += _num_crit
                num_warn += _num_warn
            except (
                vodka.exceptions.ConfigErrorUnknown,
                vodka.exceptions.ConfigErrorValue,
                vodka.exceptions.ConfigErrorType,
            ) as inst:
                if inst.level == "warn":
                    vodka.log.warn(inst.explanation)
                    num_warn += 1
                elif inst.level == "critical":
                    vodka.log.error(inst.explanation)
                    num_crit += 1

        return num_crit, num_warn

    @classmethod
    def get_attr_by_name(cls, name):
        """
        Return attribute by name - will consider value in
        attribute's `field` property
        """
        for attr_name, attr in cls.attributes():
            if attr_name == name:
                return attr
        return None

    @classmethod
    def default(cls, key_name, inst=None):
        attr = cls.get_attr_by_name(key_name)
        if not attr:
            raise KeyError("No config attribute defined with the name '%s'" % key_name)

        if attr.default and callable(attr.default):
            return attr.default(key_name, inst)
        return attr.default

    @classmethod
    def attributes(cls):
        """
        yields tuples for all attributes defined on this handler

        tuple yielded:
            name (str), attribute (Attribute)
        """

        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, Attribute):
                name = v.field or k
                yield name, v


class ComponentHandler(Handler):

    """
    This is the base config handler that will be attached to any
    vodka application or plugin
    """

    # config attribute: enabled
    enabled = Attribute(
        bool,
        default=True,
        help_text="specifies whether or not this component should be initialized and started",
    )


class InstanceHandler(Handler):

    """
    This is the config handler for the vodka main config
    """

    apps = Attribute(
        dict,
        help_text="Holds the registered applications",
        default={},
        handler=lambda k, v: vodka.app.get_application(k),
    )
    plugins = Attribute(
        list,
        help_text="Holds the registered plugins",
        default=[],
        handler=lambda k, v: vodka.plugin.get_plugin_class(v.get("type")),
    )
    data = Attribute(list, help_text="Data type configuration", default=[])
    logging = Attribute(
        dict, help_text="Python logger configuration", default={"version": 1}
    )

    @classmethod
    def configure_plugins(cls, configurator, cfg, path):
        configurator.echo("")
        configurator.echo("Configure plugins")
        configurator.echo("")
        plugin_type = configurator.prompt("Add plugin", default="skip")
        if "plugins" not in cfg:
            cfg["plugins"] = []

        while plugin_type != "skip":
            plugin_name = configurator.prompt("Name", default=plugin_type)
            try:
                plugin_class = configurator.plugin_manager.get_plugin_class(plugin_type)
                plugin_cfg = {"type": plugin_type, "name": plugin_name}
                configurator.configure(
                    plugin_cfg,
                    plugin_class.Configuration,
                    path="%s.%s" % (path, plugin_name),
                )
                cfg["plugins"].append(plugin_cfg)
            except Exception as inst:
                configurator.echo(inst)
            plugin_type = configurator.prompt("Add plugin", default="skip")

    @classmethod
    def configure_apps(cls, configurator, cfg, path):
        configurator.echo("")
        configurator.echo("Configure applications")
        configurator.echo("")

        if "apps" not in cfg:
            cfg["apps"] = {}

        name = configurator.prompt("Add application (name)", default="skip")
        while name != "skip":
            app_cfg = {}
            configurator.configure(
                app_cfg, vodka.app.Application.Configuration, path=f"{path}.{name}"
            )
            vodka.app.load(name, app_cfg)
            app = vodka.app.get_application(name)
            configurator.configure(app_cfg, app.Configuration, path=f"{path}.{name}")
            cfg["apps"][name] = app_cfg
            name = configurator.prompt("Add application (name)", default="skip")


class Config(munge.Config):
    defaults = {"config": {}, "config_dir": "~/.vodka", "codec": "yaml"}

    def read(self, config_dir=None, clear=False, config_file=None):
        """
        The munge Config's read function only allows to read from
        a config directory, but we also want to be able to read
        straight from a config file as well
        """

        if config_file:
            data_file = os.path.basename(config_file)
            data_path = os.path.dirname(config_file)

            if clear:
                self.clear()

            config = munge.load_datafile(data_file, data_path, default=None)

            if not config:
                raise OSError("Config file not found: %s" % config_file)

            munge.util.recursive_update(self.data, config)
            self._meta_config_dir = data_path
            return
        else:
            return super().read(config_dir=config_dir, clear=clear)
