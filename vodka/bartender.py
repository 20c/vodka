import os
import os.path
import inspect
import shutil
import click
import vodka
import vodka.app
import vodka.config
import vodka.config.configurator

import munge.codec.all
from munge import config as munge_config

VODKA_INSTALL_DIR = os.path.dirname(inspect.getfile(vodka))

class ClickConfigurator(vodka.config.configurator.Configurator):
    """
    Configurator class with prompt and echo wired to click
    """
    def echo(self, msg):
        click.echo(msg)

    def prompt(self, *args, **kwargs):
        return click.prompt(*args, **kwargs)


def options(f):
    """
    Shared options, used by all bartender commands
    """

    f = click.option('--config', envvar='VODKA_HOME', default=click.get_app_dir('vodka'), help="location of config file")(f)
    return f

@click.group()
@click.version_option()
def bartender():
    pass


@bartender.command()
@options
def check_config(config):
    """
    Check and validate configuration attributes, to help administrators
    quickly spot missing required configurations and invalid configuration
    values in general
    """


    cfg = vodka.config.Config(read=config)

    vodka.log.set_loggers(cfg.get("logging"))
    vodka.app.load_all(cfg)

    click.echo("Checking config at %s for errors ..." % config)

    num_crit, num_warn = vodka.config.InstanceHandler.validate(cfg)

    click.echo("%d config ERRORS, %d config WARNINGS" % (num_crit, num_warn))


@bartender.command()
@options
@click.option('--skip-defaults/--no-skip-defaults', default=False, help="skip config variables that have a default value")
def config(config, skip_defaults):
    """
    Generates configuration file from config specifications
    """

    configurator = ClickConfigurator(
        vodka.plugin, 
        skip_defaults=skip_defaults
    )

    configurator.configure(vodka.config.instance, vodka.config.InstanceHandler)
    
    try:
        dst = munge_config.parse_url(config)
    except ValueError:
        config = os.path.join(config, "config.yaml")
        dst = munge_config.parse_url(config)

    config_dir = os.path.dirname(config)
    if not os.path.exists(config_dir) and config_dir:
        os.makedirs(config_dir)

    dst.cls().dumpu(vodka.config.instance, dst.url.path)

    if configurator.action_required:
        click.echo("")
        click.echo("not all required values could be set by this script, please manually edit the config and set the following values")
        click.echo("")
        for item in configurator.action_required:
            click.echo("- %s" % item)
        click.echo("")

    click.echo("Config written to %s" % dst.url.path)



@bartender.command()
@click.option('--path', type=click.Path(), default=".", help="generate app files to this location")
def newapp(path):
    """
    Generates all files for a new vodka app at the specified location.

    Will generate to current directory if no path is specified
    """

    app_path = os.path.join(VODKA_INSTALL_DIR, "resources", "blank_app")
    if not os.path.exists(path):
        os.makedirs(path)
    elif os.path.exists(os.path.join(path, "application.py")):
        click.error("There already exists a vodka app at %s, please specify a different path" % path)
    os.makedirs(os.path.join(path, "plugins"))
    shutil.copy(os.path.join(app_path, "application.py"), os.path.join(path, "application.py"))
    shutil.copy(os.path.join(app_path, "plugins", "example.py"), os.path.join(path, "plugins", "example.py"))




@bartender.command()
@options
def serve(config):
    """
    Serves (runs) the vodka application
    """

    cfg = vodka.config.Config(read=config)
    vodka.run(cfg, cfg)

if __name__ == "__main__":
    bartender()
