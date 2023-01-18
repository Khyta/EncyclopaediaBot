# EncyclopaediaBot

![EncyclopaediaBot a r/NewToReddit project](header.jpg)

A reddit bot for r/EncyclopaediaOfReddit to provide a post-based wiki. The bot
automates the creation of and edits of posts based on the wiki to enhance reddit
mobile user experience while browsing this post-based wiki. This bot is part of
the r/NewToReddit network and managed by u/Khyta.

# Installation

This script has been tested on an Ubuntu 22.04.1 LTS machine with Python 3.10.6.
## Requirements

- Python `3.10.+`
- `praw`
- `sys`
- `os`
- `re`
- `time`
- `dotenv`

## Quick Setup

1. Clone the repository to your machine.
2. Create a `.env` file in the root directory of the project.
3. Fill out the `.env` file with the credentials from your reddit bot account.
   (See [here](https://www.reddit.com/prefs/apps) for where to find these)
4. Run the script with `python3 script.py` from your terminal.