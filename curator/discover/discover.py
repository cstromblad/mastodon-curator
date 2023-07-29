import json
import logging
import os

import click
import requests

from curator.masto_api import api
from curator.utils import utils
from curator.utils import output

# curator discover --hashtag "threatintel" --create-list --named-list "ThreatIntel"


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
@click.pass_context
def discover_cli(ctx,
                 hashtag,
                 ntoots):
    ctx.obj['command'] = 'discover'
    
    if 'MASTODON_API_ACCESS_TOKEN' in os.environ:
        access_token = os.environ['MASTODON_API_ACCESS_TOKEN']
    else:
        logging.error('Environment variable MASTODON_API_ACCESS_TOKEN is NOT present.')
        return

    if "MASTODON_INSTANCE_URL" in os.environ:
        instance_url = os.environ['MASTODON_INSTANCE_URL']
    else:
        logging.error('Environment variable MASTODON_INSTANCE_URL is NOT present.')
        return 

    api_session = api.MastodonAPI(instance_url, access_token)
    ctx.obj['api_session'] = api_session

    if hashtag:
        logging.info(f'Attempting to fetch accounts tooting about #{hashtag} (max: {ntoots} toots)')
        
        accounts = accounts_tooting_about(api_session, hashtag, ntoots)        

        ctx.obj['hashtag'] = hashtag
        ctx.obj['accounts'] = accounts
