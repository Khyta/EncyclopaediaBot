import praw
import os
import sys
import re
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'

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

def get_wiki_links(page, reddit):
  # This function gets the links inside the wiki that link to other wiki pages.
  # This function uses RegEx and requires the re module.
  # Regex expression to match the links: "\* \[[A-Z] ?-? ?[A-Z]?]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/wiki\/encyclopaedia-redditica\/[a-z]+-\d\)"gm
  sub = reddit.subreddit(sub_name)
  wiki_page = sub.wiki[page]
  wiki_links = re.findall("\* \[[A-Z] ?-? ?[A-Z]?\]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/wiki\/encyclopaedia-redditica\/[a-z]+-\d\)", wiki_page.content_md, re.MULTILINE)
  return wiki_links

def get_wiki_page(page, reddit):
  # This function gets the contents of a wiki page.
  sub = reddit.subreddit(sub_name)
  wiki_page = sub.wiki[page]
  return wiki_page.content_md

def get_post_flairs(content):
  # This function gets the submission flairs to be used from the wiki denoted as
  # ::flair_text:: in the wiki page. RegEx: "::[a-zA-Z]+::"gm
  flair_texts = re.findall("::[a-zA-Z].+::", content, re.MULTILINE)
  flair_texts = [flair.replace('::', '') for flair in flair_texts]
  return flair_texts

def get_post_titles(content):
  # This function gets the post titles to be used from the wiki denoted as h1 in
  # the wiki page. RegEx: "^# ?[a-zA-Z].+$"gm
  post_titles = re.findall("^# ?[a-zA-Z].+$", content, re.MULTILINE)
  post_titles = [title.replace('#', '') for title in post_titles]
  return post_titles

def prettify_content(content, flair, title):
  # This function removes the flair and header used for the submission itself
  # inside the wiki content.
  content = content.replace('::'+flair+'::', '')
  content = content.replace('#'+title, '')
  return content

if __name__ == '__main__':
  fetch_env()
  reddit = reddit_login()

  print('Logged in as:', reddit.user.me())

  content = get_wiki_page('2', reddit)
  flair_texts = get_post_flairs(content)
  titles = get_post_titles(content)
  # content = prettify_content(content, flair_text, title)

  print('Flair:', flair_texts)
  print('Title:', titles)