# Mastodon Prune

Necessary DISCLAIMER. This code is provided as-is. I'm not a lawyer, which means I'm not quite sure what should be put here. But this code probably, and likely has bugs.

In order to run this tool you'll need to create a "Mastodon Application" and through that get yourself an ACCESS_TOKEN. This is used to authenticate the tool. 


## Instructions

1. Navigate to Mastodon Preferences -> Development -> New application
2. Name the application something useful (like mastodon-prune)
3. Under Scopes, make sure you ONLY use the following:
- read:accounts
- read:statuses
- read:follows
- write:follows
4. Save changes
5. Copy 'Your access token' as you will need this when running the tool.

I'm using [Poetry](https://python-poetry.org/) to manage Python environments and packages, you should too.

Assuming you've installed Poetry.

1. Run `poetry shell && poetry install`

This will install a few necessary Python packages such as 'tqdm', 'requests' and 'click'. Now you're almost ready to run the tool.

2. Remember the access_token you copied, bring it forth. Invoking the tool you do this:

3. `$ MASTODON_API_ACCESS_TOKEN=<"YOUR_TOKEN"> python prune.py --help`

Hopefully the rest should be self-explanatory.

