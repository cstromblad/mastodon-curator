import logging

import click 

from curator.utils import utils
from curator.masto_api.timelines import TimelinesAPI
from curator.masto_api.accounts import AccountsAPI


def output_as_csv(ctx):

    accounts = ctx.obj['accounts']
    hashtag = ctx.obj['hashtag']
    no_bots = ctx.obj['no_bots']
    
    usernames = [account['acct'] for account in accounts]

    # Make sure the output filename represents the fact that no_bots are included.
    if no_bots:
        filename = f"{hashtag}_no_bots"

    else:
        filename = f"{hashtag}_"
    
    utils.write_mastodon_csv(filename, usernames)


def output_to_mastodon_list(ctx, list_name):
    """ Save accounts discovered in toots as a Mastodon list. """

    if 'accounts' in ctx.obj:
        if ctx.obj['accounts']:
            accounts = ctx.obj['accounts']

    if 'hashtag' in ctx.obj:
        hashtag = ctx.obj['hashtag']

    api_session = ctx.obj['api_session']
    timelines_api = TimelinesAPI(api_session.instance_url, api_session.access_token)
    accounts_api = AccountsAPI(api_session.instance_url, api_session.access_token)

    if not list_name:
        # This means user have NOT specified a list to add people to, defaulting
        # to the hashtag.

        list_name = hashtag

    # First we must follow the account, otherwise we can't add them to a list.
    for account in accounts:
        if not accounts_api.follow(account['id']):
            accounts.remove(account)
            logging.debug(f'Removed account from accounts: {account}')

            if account in accounts:
                logging.debug('Accont NOT removed?!')

    # Finally we add them to the named list.
    timelines_api.add_accounts_to_list(accounts, list_name)


def output_to_console(ctx):

    accounts = ctx.obj['accounts']
    hashtag = ctx.obj['hashtag']

    print(f'The following accounts are tooting about {hashtag}\n')

    for account in accounts:
        print(f'{account["acct"] : <40} (id: {account["id"] : ^15})')


def accounts_filter(ctx, no_bots):

    accounts = ctx.obj['accounts']
    api_session = ctx.obj['api_session']

    # First we remove any accounts wishing to be excluded from discovery.
    for account in accounts:
        if not account['discoverable']:
            logging.debug(f'Non-discoverable account removed: {account["acct"]}')
            accounts.remove(account)

        # We also need to check for "local" accounts as they will be missing
        # the "instance" part of the username.

        if utils.is_local_account(account['acct']):
            account['acct'] = f"{account['acct']}@{api_session.instance_name}"

        # Finally if the user wishes to remove bots this will do it.
        if no_bots:
            if account['bot']:
                logging.debug(f'Bot account removed: "{account["acct"]}"')
                try:
                    accounts.remove(account)
                except ValueError:
                    continue


@click.command()
@click.option('--format', 'output_format', default='csv', help="What format of output data?")
@click.option('--no-bots', is_flag=True, help="Exclude accounts identified as bots from output.")
@click.option('--list-name', default="", help="Exporting accounts to this Mastodon list.")
@click.pass_context
def manage_output(ctx,
                  output_format, 
                  no_bots, 
                  list_name) -> bool:

    if output_format.lower() == 'csv':
        logging.info('Selected output type: CSV')

    # Need to process usernames since "local" accounts will only show
    # the username, not the instance name like: username@instance.name"

    ctx.obj['no_bots'] = no_bots
    ctx.obj['output_format'] = output_format.lower()

    if not ctx.obj['command']:
        logging.error('No command have executed, aborting output command.') 
        return  

    # Remove those who don't want to be discovered, and bot-accounts if the user 
    # indicates they wish not to include them.

    accounts_filter(ctx, no_bots)

    if output_format == 'csv':
        logging.info('Output format: CSV')
        output_as_csv(ctx)

    elif output_format == "mastodon-list":
        logging.info('Output format: mastodon-list')
        if not list_name:
            list_name = ctx.obj['hashtag']

        output_to_mastodon_list(ctx, list_name)

    elif output_format == "console":
        logging.info('Output format: console')
        output_to_console(ctx)