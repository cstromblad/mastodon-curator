# Mastodon Curator

Necessary DISCLAIMER. This code is provided as-is. I'm not a lawyer, which means I'm not quite sure what should be put here. But this code probably, and likely has bugs.

In order to run this tool you'll need to create a "Mastodon Application" and through that get yourself an ACCESS_TOKEN which is used when authenticating against the Mastodon API of your instance.

## Setup and Installation

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

You will also need to export two environment variables:

- MASTODON_API_ACCESS_TOKEN
- MASTODON_INSTANCE_URL

You should set them to your ACCESS_TOKEN that you got from above, and add the name of your instance to the other variable. For example:
- `export MASTODON_INSTANCE_URL="https://swecyb.com"`



## Curator Discover
TBD

- Discover through hashtags
`curator discover --hashtag <tag> --output-csv`

This will create a list of accounts tooting about #hashtag and save it as an importable CSV-file.

## Curator Prune
TBD

Hopefully the rest should be self-explanatory.

# TODO
- Add more "parameters" used to consider an account inactive, such as: "number of followers" the followed account has. (What else would be useful?)
