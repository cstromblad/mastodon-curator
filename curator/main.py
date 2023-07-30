import logging
import os

import click
import redis

from curator.discover import discover
from curator.prune import prune
from curator.utils import output


@click.group(chain=True)
@click.option('--dry-run', is_flag=True, help="No modifications of accounts, followers etc.")
@click.pass_context
def cli(ctx, dry_run):
    
    ctx.ensure_object(dict)

    ctx.obj['dry_run'] = dry_run
    ctx.obj['redis'] = redis.Redis(host='localhost', port=6379, db=0)
    # This variable contains a sort of "state" of the currently excuting
    # command. The idea is to convey what's going on to other modules/commands
    # such as the "output" subcommand.
    ctx.obj['command'] = ""

    try:
        ctx.obj['MASTODON_API_ACCESS_TOKEN'] = os.environ['MASTODON_API_ACCESS_TOKEN']
        ctx.obj['MASTODON_INSTANCE_URL'] = os.environ['MASTODON_INSTANCE_URL']
    except KeyError:
        logging.error('MASTODON_API_ACCESS_TOKEN or MASTODON_INSTANCE_URL, or both, are missing from environment variables.')
        exit()


if __name__ == "__main__":

    logging.basicConfig(filename="logs/curator.log", encoding="utf-8", level=logging.DEBUG)

    cli.add_command(prune.prune_cli, name="prune")
    cli.add_command(discover.discover_cli, name="discover")
    cli.add_command(output.manage_output, name="output")

    cli()

    logging.shutdown()
