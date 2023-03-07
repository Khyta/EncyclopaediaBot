# EncyclopaediaBot

![EncyclopaediaBot a r/NewToReddit project](header.jpg)

A reddit bot for r/EncyclopaediaOfReddit to provide a post-based wiki. The bot
automates the creation of and edits of posts based on the wiki to enhance reddit
mobile user experience while browsing this post-based wiki. This bot is part of
the r/NewToReddit network and managed by u/Khyta.

# Features

- Automatically create a post for each h1 heading in the wiki.
- Update the corresponding post if the wiki is edited.
- Update and create flairs based on the wiki.
- Delete posts that are not in the wiki anymore.
- Convert wiki links to post links for better mobile user experience.
- The script for checking the wiki will run automatically at a statistically
  calculated time: The script will check the wiki revision times and determine a
  possible timeframe where the possibility of a collision from a current wiki
  edit while the script is running is minimal. The timeframe will be
  communicated via modmail to the subreddit moderators beforehand.

## Example

The bot is currently running on r/EncyclopaediaOfReddit. Here is an extract of a
wiki and the corresponding posts created by the bot.

![A wiki page](wiki_example.png)

![Posts created by the bot](posts_example.png)

# Installation

This script has been tested on an Ubuntu 22.04.1 LTS machine with Python 3.10.6.

## Requirements

Requirements are automatically installed when executing `./main.sh`.

## Quick Setup

1. Clone the repository to your machine using `git clone https://github.com/Khyta/EncyclopaediaBot.git`.
2. Create a `.env` file in the root directory of the project.
3. Fill out the `.env` file with the credentials from your reddit bot account.
   (See [here](https://www.reddit.com/prefs/apps) for where to find these)
4. Add your subreddit name where you want to run the bot to the `reddit_wiki_bot.py` file.
5. Specify the names of the wiki pages you want to use for the bot in the
   `reddit_wiki_bot.py` file.
6. Make the `main.sh` file executable with `chmod +x main.sh`.
7. Run the script with `./main.sh`.

# Usage

## Rebooting the bot

Simply run `./main.sh` again. The bot will automatically check for new wiki
entries and update the posts accordingly on a calculated timeframe. If you see:
`Logged in as: EncyclopaediaBot` in the terminal, the bot is running. If you
really want to make sure that the bot is running, check for a new `.log` file in
the `logs` directory with a line saying when the next wiki check will be done.

Please do not reboot the server while the bot is doing wiki checks. It should be
safe to terminate the process while the bot is in the sleeping phase and waits
until the next wiki check.

## Structure of the wiki

It is of utmost importance that the wiki is structured in a specific way. The
bot will not work otherwise. The wiki should be structured as follows:

```
#Heading
::flair_text::

Here is some filler text that will be used as the post's selftext. The h1 heading will be converted to the post's title.

## Subheading

Here is some more filler text. Subheadings are optional and will be converted one level down to create the right formatting.

- h2 -> h1
- h3 -> h2
- h4 -> h3
- etc.

#Other heading for new post
::flair_text::

The flair text has to come directly after the h1 heading. This flair text will determine the flair used for the post.
```

- The flair after the h1 heading is optional. If no flair is specified, the bot
will flair the post with a 'Missing flair' flair. 
- The bot will also create the flairs that are used in the wiki if they do not
exist yet in the subreddit.
- It is important that there is **no** space between the `#` and the heading text.
- It is also important that the `::flair_text::` comes directly after the h1
  heading.

## Limitations

The following limitations are planned to be fixed in the future.

- [x] Currently, the user has to specify which wiki page to use for the bot to work.
It is planned to automate this process in the future and include a command to
exclude specific wiki pages from the bot. 
- [x] The bot currently does not check for duplicate posts and wiki edits.
- [x] The bot does not throw an error via modmail or other reddit specific
  communications if something goes wrong.
- [x] The bot does not make periodic posts and has to be started manually.
- [x] The links between wikis are currently not translated to links between
  posts.

# Miscellaneous Scripts

There are several small python helper scripts in the `scripts` directory. These
scripts are not used actively by the bot and are only there for convenience. The
usage of the script is simply by running `python3 script_name.py` in the
terminal unless otherwise specified.

## barebones.py

This script is a barebones script that can be used to test the reddit API. It is
the base for the other scripts when I need a template to work with.

## nuker.py

Nukes all posts that are in the `post_info.csv` file. This script is useful if
you want to start over with the bot. **PLEASE BE CAREFUL WHEN USING THIS SCRIPT AS
THERE IS NO UNDO FUNCTION.**

## link_replacer.py

This is a script that was useful for converting comment links to wiki links at
the time we migrated from a comment-based wiki to a post-based wiki. It is not
used anymore and is only there for reference.

## link_helper.py

This script constructs a `.csv` file of all entries in the wiki with their
corresponding post link. This is useful if you want an overview of all wiki
entries and their corresponding post links for referencing purposes.

## flair_helper.py

Very similar to `link_helper.py`, this script constructs a `.csv` file of all
entries in the wiki with their corresponding flair. Also useful for referencing
purposes and checking if the correct flairs have been assigned to the correct
entries.

## hunter.py

Probably the most useful script as it searches through the wiki for specific
words. We used it to update links to entries where we changed the `h1` heading
of the entry. Because the bot deletes the old post and creates a new one, the
post links change and thus needed an update in the relevant wiki entries.

### Usage

1. `python3 hunter.py -s <search_term>`
2. `cat <D-M-Y H>_00.log` (best used with TAB autocomplete)

## ascii_art.py

This script was just a testing script to make the launch of the main bot script
more fancy. Not in usage currently.
  

# Credits

Without these wonderful people, this project would not have been possible.

- The [r/NewToReddit](https://www.reddit.com/r/NewToReddit/) mod team for the support and motivation.
- [u/SolariaHues](https://www.reddit.com/user/SolariaHues) for helping to overcome limitations and testing the
  bot.
- [u/Nugget_MacChicken](https://www.reddit.com/user/Nugget_MacChicken) for technical support and ideas.
- [LarsZauberer](https://github.com/LarsZauberer) on GitHub for in-depth technical support and ideas.
- [u/prettyoaktree](https://www.reddit.com/user/prettyoaktree) for technical support and ideas.