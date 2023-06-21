# This script searches for a target link name in the wiki .txt files and returns
# the headings of the entries where the link appears.

import praw
import os
import sys
import re
import time
import pandas as pd
import numpy as np
import logging as log
import datetime
import pytz
import argparse
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--search", nargs = "*", help="searches for a string in the wiki pages and returns the headings of the entries where the string appears")
args = parser.parse_args()

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

def get_post_sections(content):
    # This function iterates through the wiki content and splits up the wiki into
    # sections for later posting. Each post starts with a title (#Header)
    # and a flair (::Flair::). This function uses RegEx and requires the re
    # module.
    title_pattern = "^#[^#].*"
    flair_pattern = "::([^:]+)::"

    titles = []
    flairs = []
    posts = []

    # Iterate through the lines
    for line in content.splitlines():
        # If the line is a title
        if re.match(title_pattern, line):
            # Get the index of the next line
            nextIndex = content.splitlines().index(line)+1
            # Get the next line
            nextLine = content.splitlines()[nextIndex]
            # If the next line is a flair
            if re.match(flair_pattern, nextLine):
                # Add the title to the titles list
                titles.append(re.findall(title_pattern, line))
                # Add the flair to the flairs list
                flairs.append(re.findall(flair_pattern, nextLine))
                # Create a variable to store the post
                post = ''
                # Iterate through the lines after the flair
                for i in range(nextIndex+1, len(content.splitlines())):
                    # If the line is a title
                    if re.match(title_pattern, content.splitlines()[i]):
                        # Break the loop
                        break
                    # Add the line to the post
                    post += content.splitlines()[i] + '\n'
                # Add the post to the posts list
                posts.append(post)
            # If the next line is not a flair
            else:
                # Add the title to the titles list
                titles.append(re.findall(title_pattern, line))
                # Add the missing flair to the flairs list
                flairs.append('::Missing flair::')
                # Create a variable to store the post
                post = ''
                # Iterate through the lines after the title
                for i in range(nextIndex, len(content.splitlines())):
                    # If the line is a title
                    if re.match(title_pattern, content.splitlines()[i]):
                        # Break the loop
                        break
                    # Add the line to the post
                    post += content.splitlines()[i] + '\n'
                # Add the post to the posts list
                posts.append(post)

    titles = list(np.concatenate(titles).flat)  # Flatten the titles list
    titles = [title.strip() for title in titles]
    titles = [str(x).replace('#', '', 1) for x in titles]  # Format the titles
    flairs = [str(x).replace(':', '') for x in [flair[0] for flair in flairs]]
    # flairs = list(np.concatenate(flairs))  # Flatten the flairs list
    # Remove the first newline
    posts = [post[1:] if post.startswith('\n') else post for post in posts]
    # Remove the horizontal rule
    posts = [post.replace('---', '') for post in posts]
    # Downgrades the headers
    posts = [post.replace('##', '#') for post in posts]
    posts = [post.replace('###', '##') for post in posts]
    posts = [post.replace('####', '###') for post in posts]
    posts = [post.replace('#####', '####') for post in posts]
    posts = [post.replace('######', '#####') for post in posts]

    return posts, titles, flairs

def get_wiki_page(reddit, wiki_page_id):
    # This function gets the content of a wiki page and returns it as a string.
    # Requires the praw module.
    wiki_page = reddit.subreddit(sub_name).wiki[wiki_page_id]
    content = wiki_page.content_md
    return content

def search_link(reddit, link_name, content):
    # This function searches for a target link name in all wiki .txt files and
    # returns the heading where they appear.
    pass

def handle_wiki_page(wiki_page_id, reddit, link_name):
    # This function handles a wiki page. It gets the content of the wiki page,
    # splits it up into sections, and checks if a certain link is present in the
    # specific section and returns the heading where it appears.
    # Requires the praw module.
    content = get_wiki_page(reddit, wiki_page_id)
    posts, titles, flairs = get_post_sections(content)
    matches = []
    for post, title, flair in zip(posts, titles, flairs):
        if link_name in post:
            matches.append(title)   
    return matches
    
    

def main():
    fetch_env()
    try:
        reddit = reddit_login()
    except Exception as e:
        log.error(f"Error logging in: {e}. Trying again in 5 minutes")
        time.sleep(300)
        reddit = reddit_login()

    print('Logged in as:', reddit.user.me())

    # List of wiki page IDs to process
    wiki_page_ids = ['index/all-entries', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if args.search:
        for i in range(len(args.search)):
            link_name = args.search[i]
    else:
        link_name = 'Llama'

    t0 = time.time()
    for page_id in wiki_page_ids:
        try:
            result = handle_wiki_page(page_id, reddit, link_name)
            for section in result: # iterate over the generator using a for loop
                log.info(f"Found '{link_name}' in wiki page '{page_id}' in section '{section}'")
        except Exception as e:
            log.error(f"Error handling wiki page: {e}")
            result = None
    t1 = time.time()
    log.info(f"Finished in {round(t1-t0, 3)} seconds")
    print('Done, check the log file')

    

if __name__ == '__main__':
    main()
