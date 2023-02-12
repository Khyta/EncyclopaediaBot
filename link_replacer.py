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

now = datetime.datetime.now(pytz.UTC)
filename = now.strftime("%d-%m-%Y %H_00") + '.log'

logger = log.getLogger()
logger.setLevel(log.INFO)
handler = log.FileHandler(filename)
handler.setLevel(log.INFO)
formatter = log.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S %Z')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
    
def url_encoding(heading):
    # This function converts the heading that may contain special characters in
    # a reddit post link to a format that can be used in a wiki link. For
    # example, it will convert / to .2F. Sadly the percent encoding does not
    # work as reddit uses . instead of % for some reason.
    heading = heading.lower()
    heading = heading.replace(' ', '_')
    heading = heading.replace('/', '.2F')
    heading = heading.replace('\\', '.5C')
    heading = heading.replace('?', '.3F')
    heading = heading.replace('!', '.21')
    heading = heading.replace('“', '.201C')
    heading = heading.replace('”', '.201D')
    heading = heading.replace('"', '.22')
    heading = heading.replace("'", '.27')
    heading = heading.replace('’', '.2019')
    heading = heading.replace('`', '.60')
    heading = heading.replace('@', '.40')
    heading = heading.replace(':', '.3A')
    heading = heading.replace(';', '.3B')
    heading = heading.replace('(', '.28')
    heading = heading.replace(')', '.29')
    heading = heading.replace(',', '.2C')
    heading = heading.replace('#', '.23')
    heading = heading.replace('~', '.7E')
    heading = heading.replace('$', '.24')
    heading = heading.replace('%', '.25')
    heading = heading.replace('&', '.26amp.3B')
    heading = heading.replace('+', '.2B')
    heading = heading.replace('<', '.26lt.3B')
    heading = heading.replace('>', '.26gt.3B')
    heading = heading.replace('=', '.3D')
    heading = heading.replace('{', '.7B')
    heading = heading.replace('}', '.7D')
    heading = heading.replace('[', '.5B')
    heading = heading.replace(']', '.5D')
    heading = heading.replace('^', '.5E')
    heading = heading.replace('|', '.7C')

    return heading

def replace_links(content):
    # This function replaces all the links that lead to a comment section with
    # the corresponding wiki link. The first character of the link text dictates
    # in which wiki page the link should be placed.
    new_content = content

    # This regex matches all the links that link to a comment section.
    regex = r'\[(.*?)\]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/comments\/qbb173[^\)]+\)'
    matches = re.finditer(regex, content)
    log.info(f'{matches}')

    for match in matches:
        complete_link = match.group(0)
        # log.info(f'Complete link: {complete_link}')
        link_text = match.group(1)
        # log.info(f'Link text: {link_text}')

        converted_link_text = url_encoding(link_text)
        # log.info(f'Converted link text: {converted_link_text}')

        # Idea: Work with the complete_link to get the first character for the
        # mapping. Use RegEx to get the first character of the complete_link. 
        pattern = re.compile(r'[a-zA-Z]')
        first_char = pattern.search(complete_link)
        first_char = first_char.group(0)
        # log.info(f'First character: {first_char}')
    
        first_char = first_char.upper()
        if first_char in mapping: # BUG this does not take into consideration the case where the first character is not in the alphabet
            new_link_text = f'[{link_text}](https://www.reddit.com/r/EncyclopaediaOfReddit/wiki/{mapping[first_char]}/#wiki_{converted_link_text})'
            log.info(f'New link text: {new_link_text}')
            new_content = new_content.replace(complete_link, new_link_text)
        else:
            pass

    return new_content


def handle_wiki_page(page_id, reddit):
    # The main function that handles the wiki page.

    content = get_wiki_page(reddit, page_id)

    new_content = replace_links(content)
    # log.info(f'New content: {new_content}')

    reddit.subreddit(sub_name).wiki[page_id].edit(content=new_content)
    print(f'Edited wiki page {page_id}.')

if __name__ == '__main__':
    fetch_env()
    reddit = reddit_login()

    print('Logged in as:', reddit.user.me())

    wiki_page_ids = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

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
