import logging

from datetime import datetime


def write_mastodon_csv(filename, usernames) -> None:

    date = datetime.isoformat(datetime.utcnow())
    
    logging.info(f'Saving output as: {filename}_{date}.csv')
    with open(f"{filename}_{date}.csv", "w") as fd:
        fd.write(f"Account address,Show boosts,Notify on new posts,Languages\n")

        for user in usernames:
            fd.write(f"{user},True,False,\n")


def is_local_account(account) -> bool:

    if "@" not in account:
        return True

    return False