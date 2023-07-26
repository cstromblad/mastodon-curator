# Mastodon Prune

Necessary DISCLAIMER. This code is provided as-is. I'm not a lawyer, which means I'm not quite sure what should be put here. But this code probably, and likely has bugs.

In order to run this tool you'll need to create a "Mastodon Application" and through that get yourself an ACCESS_TOKEN. This is used when authenticating against the Mastodon API using the tool.


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

Now you actually have to modify two things in prune.py:
1. BASE_URL
2. INSTANCE_NAME

Change BASE_URL to the "home" address of your current instance, ie "https://infosec.exchange".
Change INSTANCE_NAME to your current instance "infosec.exchange".

Yeah, I realize as I read this how stupid this is. I will change this soon enough to make more sense. This is the first version of the prune tool.

I'm using [Poetry](https://python-poetry.org/) to manage Python environments and packages, you should too.

Assuming you've installed Poetry.

1. Run `poetry shell && poetry install`

This will install a few necessary Python packages such as 'tqdm', 'requests' and 'click'. Now you're almost ready to run the tool.

2. Remember the access_token you copied, bring it forth. Invoking the tool you do this:

3. `$ MASTODON_API_ACCESS_TOKEN=<"YOUR_TOKEN"> python prune.py --help`

Hopefully the rest should be self-explanatory.

# TODO

- Make BASE_URL a cmdline option instead, and get INSTANCE_NAME from this option instead of keeping it in the code. 
- Add more "parameters" used to consider an account inactive, such as: "number of followers" the followed account has. (What else would be useful?)
