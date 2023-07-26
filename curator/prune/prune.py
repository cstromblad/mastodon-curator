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

def api_bootstrap() -> (requests.Session, str):

    try:
        ACCESS_TOKEN = os.environ['MASTODON_API_ACCESS_TOKEN']
    except KeyError:
        print("Aborting, you have forgotten to set the MASTODON_API_ACCESS_TOKEN!")
        exit(-1)
    
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    
    s = requests.Session()
    s.headers = headers

    account_id = verify_credentials(s)

    if not account_id:
        print("Failed to verify credentials. Not sure why, perhaps you've set the wrong API_KEY?")
        exit(-1)

    return (s, account_id)


def account_following_count(api_session, account_id) -> int:

    URL = f"{BASE_URL}/api/v1/accounts/{account_id}"

    response = api_session.get(URL)
    account = json.loads(response.text)

    return account['following_count']


def account_following(api_session, account_id, url=None) -> list:

    if not url:
        URL = f"{BASE_URL}/api/v1/accounts/{account_id}/following"
    else:
        URL = url
    params = {"limit": 80}

    response = api_session.get(URL,params=params)

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


def remove_following_account(api_session, account_id) -> str:

    API_ENDPOINT = f"{BASE_URL}/api/v1/accounts/{account_id}/unfollow"

    response = api_session.post(API_ENDPOINT)

    if response.status_code == 200:
        return account_id
        
    elif response.status_code == 403:
        print("ABORTING. Likely incorrect permissions set on ACCESS_TOKEN.")
        exit(0)

    return ""


def account_all_following(api_session,
                          account_id) -> list:

    all_accounts = []

    (accounts, next_page, prev_page) = account_following(api_session, account_id)
    all_accounts.extend(accounts)

    while next_page:

        (accounts, next_page, prev_page) = account_following(api_session, account_id, next_page)
        all_accounts.extend(accounts)

    return all_accounts


def account_toots(api_session, 
                  account_id) -> list:

    URL = f"/api/v1/accounts/{account_id}/statuses"

    response = api_session.get(BASE_URL + URL, headers=headers)

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


def prune_accounts(api_session, for_realz, max_age):

    accounts = account_all_following(api_session, account_id)

    logging.info(f'Accounts with no toots in ({max_age}) days will be considered inactive.')

    passive_accounts = []
    for account in accounts:
        if consider_inactive_account(account['last_status_at'], max_age):
            
            if is_local_account(account['acct']):
                username = f"{account['acct']}@{INSTANCE_NAME}"
            else:
                username = account['acct']

            passive_accounts.append({'id': account['id'],
                                    'username': username})
    
    save_pruned_users_as_csv(passive_accounts)

    # Now we're getting serious... pruning time!
    if for_realz:
        prune_passive_accounts(s, passive_accounts)


@click.command(context_settings={"show_default": True})
@click.option('--dry-run', is_flag=True, default=True, help="Perform dry-run, will output CSV of users that would be pruned.")
@click.option('--max-age', default=120, help="How long ago is, at most, an acceptable passive tooting time?")
def prune_cli(for_realz, dry_run, max_age, follow_account, unfollow_account):

    api_session = api.MastodonAPI("https://swecyb.com", "CTWicHygcpmtgZgvHPMjzAgF9HCGipzS37JPAidc70I")

    if dry_run:
        print("Dry run only. Saving CSV of would-be-removed accounts.\n")
        prune_accounts(api_session, max_age)

    else:
        response = input("Are you really sure? [yN] > ")

        if response.lower() == "y":
            prune_accounts(api_session, max_age)
