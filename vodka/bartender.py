import click
import vodka
import vodka.config

def options(f):
    """
    Shared options, used by all bartender commands
    """

    f = click.option('--config', envvar='VODKA_HOME', default=click.get_app_dir('vodka'))(f)
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

    # check app config

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
