from datetime import datetime


def write_mastodon_csv(filename, usernames) -> None:

    date = datetime.isoformat(datetime.utcnow())
    
    with open(f"{filename}_{date}.csv", "w") as fd:
        fd.write(f"Account address,Show boosts,Notify on new posts,Languages\n")

        for user in usernames:
            fd.write(f"{user},True,False,\n")

