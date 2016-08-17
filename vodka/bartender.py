import os
import os.path
import click
import vodka
import vodka.config
import vodka.config.configurator

import munge.codec.all
from munge import config as munge_config

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
    vodka.load(cfg.get("home","."))

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
@options
def serve(config):
    """
    Serves (runs) the vodka application
    """

    cfg = vodka.config.Config(read=config)
    vodka.run(cfg, cfg)

if __name__ == "__main__":
    bartender()
