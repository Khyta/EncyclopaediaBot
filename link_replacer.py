import praw
import os
import sys
import re
import time
import csv
import glob
import pandas as pd
import numpy as np
import hashlib
import logging as log
import datetime
import pytz
import statistics
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'


def fetch_env():
    # This function tries to fetch the environment variables and throws an error
    # if it couldn't find them. Requires the python-dotenv module.
    try:
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        user_agent = os.getenv('USER_AGENT')
        username = os.getenv('REDDIT_USERNAME')
        password = os.getenv('PASSWORD')
    except KeyError:
        log.error('Could not find environment variables.')
        sys.exit(1)
    return client_id, client_secret, user_agent, username, password


def reddit_login():
    # This function logs you in to Reddit. Requires the praw module.
    client_id, client_secret, user_agent, username, password = fetch_env()
    reddit = praw.Reddit(
        client_id=client_id,
        user_agent=user_agent,
        client_secret=client_secret,
        username=username,
        password=password
    )
    return reddit

def get_wiki_page(reddit, page_id):
    # This function gets the wiki page with the given ID.
    page = reddit.subreddit(sub_name).wiki[page_id]
    return page.content_md
    

def replace_links(content):
    # This function replaces all the links that link to a comment section to a
    # wiki link based on the first text character of the link text (excluding
    # special characters).
    new_content = content

    # This regex matches all the links that link to a comment section.
    regex = r'/\[([^\[\]]+)\]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/comments\/qbb173[^\)]+\)/gm'
    matches = re.findall(regex, content)

    for match in matches:
        # This regex matches all the special characters at the beginning of the
        # link text.
        regex = r'^[^a-zA-Z]+'
        special_chars = re.findall(regex, match)

        # This regex matches all the characters that are not special characters
        # at the beginning of the link text.
        regex = r'[^a-zA-Z]+(.+)'
        link_text = re.findall(regex, match)

        if link_text:
            # If the link text contains any characters that are not special
            # characters, then we can use the first character of the link text
            # to replace the link.
            link_text = link_text[0]
            first_char = link_text[0].upper()
            if first_char in mapping:
                # If the first character of the link text is a letter, then we
                # can replace the link with a wiki link.
                new_link = f'[{match}](https://www.reddit.com/r/EncyclopaediaOfReddit/wiki/{mapping[first_char]})'
                new_content = new_content.replace(match, new_link)
            else:
                pass
        else:
            pass

    return new_content

def handle_wiki_page(page_id, reddit):
    # The main function that handles the wiki page.

    content = get_wiki_page(reddit, page_id)

    new_content = replace_links(content)

    reddit.subreddit(sub_name).wiki[page_id].edit(new_content)

if __name__ == '__main__':
    fetch_env()
    reddit = reddit_login()

    print('Logged in as:', reddit.user.me())

    wiki_page_ids = ['1']

    mapping = {
        "A": 2,
        "B": 3, "C": 3, "D": 3, "E": 3,
        "F": 4, "G": 4, "H": 4, "I": 4, "J": 4, "K": 4, "L": 4,
        "M": 5, "N": 5, "O": 5, "P": 5, "Q": 5,
        "R": 6,
        "S": 7,
        "T": 8,
        "U": 9, "V": 9, "W": 9, "X": 9, "Y": 9, "Z": 9
    }

    for page_id in wiki_page_ids:
        handle_wiki_page(page_id, reddit)
