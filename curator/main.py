import logging

import click

from curator.discover import discover
from curator.prune import prune
from curator.utils import output
from curator.account import account


@click.group(chain=True)
@click.option('--dry-run', is_flag=True, help="No modifications of accounts, followers etc.")
@click.pass_context
def cli(ctx, dry_run):
    
    ctx.ensure_object(dict)

    ctx.obj['dry_run'] = dry_run

    # This variable contains the state
    ctx.obj['command'] = ""


if __name__ == "__main__":

    logging.basicConfig(filename="logs/curator.log", encoding="utf-8", level=logging.DEBUG)

    cli.add_command(prune.prune_cli, name="prune")
    cli.add_command(discover.discover_cli, name="discover")
    cli.add_command(output.manage_output, name="output")
    cli.add_command(account.account, name="account")

    cli()

    logging.shutdown()
