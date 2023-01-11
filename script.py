import praw
import os
import sys
import re
from dotenv import load_dotenv

load_dotenv()

sub_name = 'NewToReddit'

def fetch_env():
  # This function tries to fetch the environment variables and throws an error
  # if it couldn't find them. Requires the dotenv module.
  try:
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    user_agent = os.getenv('USER_AGENT')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('PASSWORD')
  except KeyError:
    print('[error]: Missing environment variable(s)')
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

def get_wiki_links(page):
  # This function gets the links inside the wiki that link to other wiki pages.
  # This function uses RegEx and requires the re module.
  # Regex expression to match the links: "\* \[[A-Z] ?-? ?[A-Z]?]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/wiki\/encyclopaedia-redditica\/[a-z]+-\d\)"gm
  reddit = reddit_login()
  sub = reddit.subreddit(sub_name)
  wiki_page = sub.wiki[page]
  wiki_links = re.findall("\* \[[A-Z] ?-? ?[A-Z]?\]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/wiki\/encyclopaedia-redditica\/[a-z]+-\d\)", wiki_page.content_md, re.MULTILINE)
  return wiki_links

def get_wiki_page(page):
  # This function gets the contents of a wiki page.
  reddit = reddit_login()
  sub = reddit.subreddit(sub_name)
  wiki_page = sub.wiki[page]
  return wiki_page.content_md

if __name__ == '__main__':
  fetch_env()
  reddit = reddit_login()

  print('Logged in as:', reddit.user.me())

  # print(get_wiki_page('encyclopaedia-redditica'))
  print(get_wiki_links('encyclopaedia-redditica')[0])