import logging
import json
import os

from collections import Counter
from datetime import datetime

from tqdm import tqdm
import click
import requests

from curator.masto_api import api


PRUNED_USERS_CSV = "pruned_passive_users"


def account_following_count(api_session) -> int:

    URL = f"/api/v1/accounts/{api_session.account_id}"

    response = api_session.session.get(api_session.instance_url + URL)
    account = json.loads(response.text)

    return account['following_count']


def account_following(api_session, url=None) -> list:

    if not url:
        URL = f"{api_session.instance_url}/api/v1/accounts/{api_session.account_id}/following"
    else:
        URL = url
    params = {"limit": 80}

    response = api_session.session.get(URL, params=params)

    links = requests.utils.parse_header_links(response.headers['link'])
    
    # FIXME: Not sure if this is the appropriate way to figure out pagination
    # pages, but it works.

    if links[0]['rel'] == 'next':
        next_page = links[0]['url']
        prev_page = links[1]['url']
    else:
        next_page = None
        prev_page = links[0]['url']

    accounts = json.loads(response.text)

    return (accounts, next_page, prev_page)


def remove_following_account(api_session, following_id) -> str:

    API_ENDPOINT = f"/api/v1/accounts/{following_id}/unfollow"

    response = api_session.session.post(api_session.instance_url + API_ENDPOINT)

    if response.status_code == 200:
        return response.text
        
    elif response.status_code == 403:
        logging.info("ABORTING. Likely incorrect permissions set on ACCESS_TOKEN.")

    return ""


def account_all_following(api_session) -> list:

    all_accounts = []

    (accounts, next_page, prev_page) = account_following(api_session)
    all_accounts.extend(accounts)

    while next_page:

        (accounts, next_page, prev_page) = account_following(api_session, next_page)
        all_accounts.extend(accounts)

    return all_accounts


def account_toots(api_session) -> list:

    URL = f"/api/v1/accounts/{api_session.account_id}/statuses"

    response = api_session.session.get(api_session.instance_url + URL)

    jd = json.loads(response.text)

    toots = []
    
    if len(jd) > 0:
        for toot in jd:
            toots.append({"id": toot["id"],
                          "created_at": toot["created_at"]})

    return toots


def last_toot(toots) -> dict:

    if len(toots) > 0:
        return toots[0]

    return {}


def consider_inactive_account(last_toot, days=120) -> bool:

    if not last_toot:
        return False

    created_at = datetime.strptime(last_toot, '%Y-%m-%d')
    delta = datetime.now() - created_at

    if delta.days > days:
        return True

    return False


def is_local_account(account) -> bool:

    if "@" not in account:
        return True

    return False


def prune_passive_accounts(api_session,
                           accounts):

    pbar = tqdm(total=len(accounts))
    for account in accounts:
        remove_following_account(api_session, account['id'])
        pbar.update(1)


def save_pruned_users_as_csv(accounts,
                             show_boosts=True,
                             notify_on_posts=False,
                             languages="") -> None:

    date = datetime.isoformat(datetime.utcnow())
    with open(f"{PRUNED_USERS_CSV}_{date}.csv", "w") as fd:
        fd.write(f"Account address,Show boosts,Notify on new posts,Languages\n")
        for account in accounts:
            username = account['username']
            fd.write(f"{username},{show_boosts},{notify_on_posts},{languages}\n")


def prune_accounts(api_session, dry_run, max_age):

    if not api_session.validate_credentials():
        logging.error("Couldn't validate credentials, exiting...")
        exit(-1)

    accounts = account_all_following(api_session)

    logging.info(f'Accounts with no toots in ({max_age}) days will be considered inactive.')

    passive_accounts = []
    for account in accounts:
        if consider_inactive_account(account['last_status_at'], max_age):
            
            if is_local_account(account['acct']):
                instance_name = os.environ['MASTODON_INSTANCE_URL'].split('://')[1]
                username = f"{account['acct']}@{instance_name}"
            else:
                username = account['acct']

            passive_accounts.append({'id': account['id'],
                                    'username': username})
    
    save_pruned_users_as_csv(passive_accounts)

    # Now we're getting serious... pruning time!
    if not dry_run:
        logging.info('Pruning accounts...')
        prune_passive_accounts(api_session, passive_accounts)


@click.command(context_settings={"show_default": True})
@click.option('--dry-run', is_flag=True, help="Perform dry-run, will output CSV of users that would be pruned.")
@click.option('--max-age', default=120, help="How long ago is, at most, an acceptable passive tooting time?")
def prune_cli(dry_run, max_age):

    if "MASTODON_API_ACCESS_TOKEN" in os.environ:
        access_token = os.environ['MASTODON_API_ACCESS_TOKEN']

    if "MASTODON_INSTANCE_URL" in os.environ:
        instance_url = os.environ['MASTODON_INSTANCE_URL']

    api_session = api.MastodonAPI(instance_url, access_token)
    logging.debug(f"{api_session.instance_url} {api_session.session.headers}")

    if dry_run:
        logging.info("Dry run only. Saving CSV of would-be-removed accounts.\n")
        prune_accounts(api_session, dry_run, max_age)

    else:
        response = input("Are you really sure? [yN] > ")

        if response.lower() == "y":
            prune_accounts(api_session, dry_run, max_age)
