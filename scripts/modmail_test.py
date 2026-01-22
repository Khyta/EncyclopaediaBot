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
import argparse
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'

minute_delay = 5

second_delay = 5

fractional_delay = second_delay/100

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--force", nargs="*", help="force testing debug state with an optional list for post IDs")
args = parser.parse_args()

now = datetime.datetime.now(pytz.UTC)
filename = now.strftime("%d-%m-%Y") + '.log'

logger = log.getLogger()
logger.setLevel(log.INFO)
handler = log.FileHandler('logs/'+filename)
handler.setLevel(log.INFO)
formatter = log.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S %Z')
handler.setFormatter(formatter)
logger.addHandler(handler)

def fetch_env():
    # This function tries to fetch the environment variables and throws an error
    # if it couldn't find them. Requires the python-dotenv module.
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
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
    try:
        client_id, client_secret, user_agent, username, password = fetch_env()
        reddit = praw.Reddit(
            client_id=client_id,
            user_agent=user_agent,
            client_secret=client_secret,
            username=username,
            password=password
        )
        return reddit
    except Exception as e:
        log.error(f"Error logging in to Reddit: {e}. Trying again in 1 hour.")
        time.sleep(3600)
        reddit_login()

def send_modmail(reddit, header, content):
    # This function sends a modmail to the moderators of the subreddit.
    # The content is the message that will be sent.
    try:
        subreddit = reddit.subreddit(sub_name)
        subreddit.message(subject=header, message=content)
    except Exception as e:
        log.error(f"Error sending modmail: {e}")
        user_message(reddit, "khyta", header, content)

def user_message(reddit, username, header, content):
    # This function sends a direct message to a specific user as backup when modmail fails
    try:
        reddit.redditor(username).message(subject=header, message=content)
        log.info(f"Message sent to user {username}")
    except Exception as e:
        log.error(f"Error sending message to user {username}: {e}")

reddit = reddit_login()
send_modmail(reddit, "Test Subject", "This is a test message to see if modmail still works the way it does via PRAW.")
