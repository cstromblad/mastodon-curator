import logging

import click

from curator.discover import discover
from curator.masto_api import api
from curator.prune import prune


@click.group()
def cli():
    pass


if __name__ == "__main__":

    logging.basicConfig(filename="logs/curator.log", encoding="utf-8", level=logging.DEBUG)

    cli.add_command(prune.prune_cli, name="prune")
    cli.add_command(discover.discover_cli, name="discover")
    cli()

    logging.shutdown()
