import json
import logging
import os

import click
import requests

from curator.masto_api import api
from curator.utils import utils

# curator discover --hashtag "threatintel" --create-list --named-list "ThreatIntel"


def named_list_exists(api_session, named_list) -> bool:

    API_ENDPOINT = f"{BASE_URL}/api/v1/lists"

    response = api_session.get(API_ENDPOINT)

    jd = json.loads(response.text)

    for l in jd:

        if named_list in l['title']:
            return True
    
    return False


def create_named_list(api_session, named_list) -> int:

    API_ENDPOINT = f"{BASE_URL}/api/v1/lists"

    data = json.dumps({'title': named_list})
    response = api_session.post(API_ENDPOINT, json=data)

    return response.status_code


def get_named_list(api_session, named_list) -> dict:

    if not named_list_exists(api_session, named_list):
        create_named_list(api_session, named_list)

    API_ENDPOINT = f"{BASE_URL}/api/v1/lists"

    response = api_session.get(API_ENDPOINT)

    if response.status_code == 200:
        jd = json.loads(response.text)

        for li in jd:

            if named_list in li['title']:
                return li

    return {}


def add_accounts_to_named_list(api_session, accounts, named_list) -> int:

    li = get_named_list(api_session, named_list)

    API_ENDPOINT = f"{BASE_URL}/api/v1/lists/{li['id']}/accounts"

    ids = list(set([account['id'] for account in accounts]))

    data = json.dumps({'account_ids': ids})
    
    response = api_session.post(API_ENDPOINT, json=data)
    
    return response.status_code

def toots_from_page(api_session, hashtag, url=None) -> list:

    if url: 
        URL = url
    else:
        URL = f"{api_session.instance_url}/api/v1/timelines/tag/{hashtag}"

    params = {"limit": 40}

    response = api_session.session.get(URL, params=params)

    if 'link' not in response.headers:
        return (None, None, None)
    
    links = requests.utils.parse_header_links(response.headers['link'])

    # FIXME: Not sure if this is the appropriate way to figure out pagination
    # pages, but it works.

    if links[0]['rel'] == 'next':
        next_page = links[0]['url']
        prev_page = links[1]['url']
    else:
        next_page = None
        prev_page = links[0]['url']

    toots = json.loads(response.text)

    return (toots, next_page, prev_page)


def toots_from_tag(api_session,
                   hashtag,
                   ntoots) -> list:

    all_toots = []

    (toots, next_page, prev_page) = toots_from_page(api_session, hashtag)
    all_toots.extend(toots)

    while True:
        (toots, next_page, prev_page) = toots_from_page(api_session,
                                                        hashtag,
                                                        next_page)
        if len(all_toots) > ntoots:
            break
        elif not next_page:
            break

        all_toots.extend(toots)
        logging.debug(f'Current length of toots({len(all_toots)})')

    return all_toots


def accounts_tooting_about(api_session, hashtag, ntoots) -> list:

    toots = toots_from_tag(api_session, hashtag, ntoots)

    temp_accounts = [toot['account'] for toot in toots]

    accounts = list({account['acct']:account for account in temp_accounts}.values())
    logging.debug(f'Created list of accounts with len({len(accounts)}))')
    return accounts


@click.command()
@click.option('--hashtag', default=None, help="Discover accounts tooting about the specific hashtags.")
@click.option('--ntoots', default=40, help="How many toots should we fetch?")
@click.option('--create-list', is_flag=True, default=False, help="Should we create a list of users based on the search?")
@click.option('--named-list', default=None, help="To which list should users be added?")
@click.option('--dry-run', is_flag=True, help="Do everything... almost.")
@click.option('--follow-account', default=None, help="Which account should be followed?")
@click.option('--unfollow-account', default=None, help="Which account should be unfollowed?")
@click.option('--output-csv', is_flag=True, help="Output as importable CSV-file.")
@click.option('--no-bots', is_flag=True, help="Exclude accounts identified as bots from output.")
def discover_cli(hashtag,
                 ntoots, 
                 create_list, 
                 named_list, 
                 dry_run, 
                 follow_account, 
                 unfollow_account,
                 output_csv,
                 no_bots):

    if 'MASTODON_API_ACCESS_TOKEN' in os.environ:
        access_token = os.environ['MASTODON_API_ACCESS_TOKEN']

    if "MASTODON_INSTANCE_URL" in os.environ:
        instance_url = os.environ['MASTODON_INSTANCE_URL']

    api_session = api.MastodonAPI(instance_url, access_token)

    if follow_account:
        if dry_run:
            logging.info(f'DRY-RUN > Would follow account: {follow_account}.')
        else:
            api_session.follow_account(follow_account)
        return 

    elif unfollow_account:
        if dry_run:
            logging.info(f'Would unfollow account: {unfollow_account}.')
        else:
            api_session.unfollow_account(unfollow_account)

        return

    if hashtag:
        logging.info(f'Attempting to fetch accounts tooting about #{hashtag} (max: {ntoots} toots)')
        accounts = accounts_tooting_about(api_session, hashtag, ntoots)

        if output_csv:
            # Need to process usernames since "local" accounts will only show
            # the username, not the instance name like: username@instance.name"

            for account in accounts:
                if utils.is_local_account(account['acct']):
                    account['acct'] = f"{account['acct']}@{api_session.instance_name}"

                if no_bots:
                    if account['bot']:
                        accounts.remove(account)
                        logging.debug(f'Bot account removed: "{account["acct"]}"')
            
            usernames = [account['acct'] for account in accounts]

            if no_bots:
                filename = f"{hashtag}_no_bots_"

            else:
                filename = f"{hashtag}_"
            
            utils.write_mastodon_csv(filename, usernames)        

    """
    toots = toots_from_tag(s, hashtag, ntoots)

    accounts = {}
    follow_accounts = []
    
    for toot in toots:

        account = toot['account']['acct']
        if account in accounts:
            accounts[account] += 1
        else:
            accounts[account] = 1

        follow_accounts.append(toot['account'])

    if create_list:
        for account in follow_accounts:
            follow_account(s, account['id'])

        add_accounts_to_named_list(s, follow_accounts, named_list)

    """