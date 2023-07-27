Disclaimer. Python is my choice for coding, but you should know that I do this as a hobby, and I'm not particularly good. I dabble, and I cobble things together through trial and error. There are currently NO tests, and bugs will be present. The tool is provided as-is, and I definitely do not guarantee the tool to work in all situations.

## About Mastodon Curator
The Mastodon Curator tool was built to manage, to curate, your timelines, accounts you follow, and to help you discover interesting accounts and people to follow.

Curator is built around subcommands, for example `discover` which you can invoke to help you explore hashtags, and accounts you already follow. Then you have the `prune` command which will help you remove inactive accounts you are following, or perhaps "shape" your followers.

## Architecture
Architecturally I've arranged Curator around modules and packages. At the bottom there's the `masto_api` module containing some fundamental core functions to manage and abstract the network layer and interaction with the [Mastodon API](https://docs.joinmastodon.org/client/intro/).

Then further up the abstraction layer you've got modules such as `discover` and `prune`.

And then finally there's `curator` bringing these modules together into the program you're reading about now.

## Setup and Installation

For management of Python environments I use [`poetry`](https://python-poetry.org/) and so should you, it really is quite awesome. Install it and once you're done, continue reading.

At this time you can only use Curator in one way, by cloning the repo and entering a `poetry shell` environment and executing Curator from there. This will change soon enough and I will provide a `--user` type installation (`pip3 install <package>`).

1. Clone the repository to an appropriate location.
2. Run `poetry install && poetry shell`

This gives you the basics, but now you also have to apply some special tactics. First you need to create a Mastodon Application `Preferences -> Development -> New application`. You need to add the following scopes:

read:
- read:follows
- read:lists
- read:accounts
- read:search
- read:statuses

write:
- write:follows
- write:lists

Create the application and at the top you now have an `Your access token` field available. Copy this value into an environment variable like this:

`$ export MASTODON_API_ACCESS_TOKEN="<your token>"`

You also have to export the name of your instance like this:

`$ export MASTODON_INSTANCE_URL="https://swecyb.com"`

Having completed this little setup-process you should be all set and ready to ... find other tooters.

You can run Curator by doing `python curator/main.py --help` and you should be able to use the tool.

## Usage

### Discovery
A common use-case is to discover accounts, or people, to follow. One way of doing this is by exploring particular `#hashtags`. Curator enables this through the subcommand `discover`. Let's say you are interested in learning about people tooting about `#physics`.

To generate an importable CSV-file of accounts tooting about `#physics` you would use Curator like this:

`$ curator discover --hashtag physics --output-csv` 

This will produce a CSV-file in the current working directory which you can then upload to, or share on, Mastodon.

### Pruning
Another common use-case is to `prune` accounts you follow, or even your followers. Doing this in Curator is a simple process.

`$ curator prune --max-age 90 --dry-run`

This will produce a list of accounts that would be pruned, but not actually prune them due to the `--dry-run` flag. Should you wish to prune accounts you follow simply remove the `--dry-run` flag and the accounts will be removed. A CSV will still be produced of the accounts pruned in case you ... by accident initiate pruning.

Currently no other method besides "last toot" (max-age) can be used to determine which accounts should be pruned. Let me know if you think of useful ways to prune accounts besides the activity of an account.

## Todo
- Provide an `pip`-installable version of Curator.
