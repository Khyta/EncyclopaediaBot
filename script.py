import praw
import os
import sys
import re
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

def check_post_flairs(titles, flair_texts):
  # This function checks whether there are the same amount of flairs as there
  # are post titles available. If not, this function will fill the flairs list
  # with empty flairs.
  if len(titles) > len(flair_texts):
    for i in range(len(titles) - len(flair_texts)):
      flair_texts.append('Missing flair')
  return flair_texts

def get_post_titles(content):
  # This function gets the post titles to be used from the wiki denoted as h1 in
  # the wiki page. RegEx: "^# ?[a-zA-Z].+$"gm
  post_titles = re.findall("^# ?[a-zA-Z].+$", content, re.MULTILINE)
  post_titles = [title.replace('#', '') for title in post_titles]
  return post_titles

def split_content(content, flairs):
  # This function splits the wiki content up at each title and then
  # removes the flair and header used for the submission itself inside the wiki
  # content.
  contents = re.split(r"#[a-zA-Z]+ ?[a-zA-Z]+\n", content, re.MULTILINE)
  contents = [content.replace('::'+flairs+'::', '') for content in contents]
  return contents

if __name__ == '__main__':
  fetch_env()
  reddit = reddit_login()

  print('Logged in as:', reddit.user.me())

  content = get_wiki_page('2', reddit)
  flair_texts = get_post_flairs(content)
  titles = get_post_titles(content)

  flair_texts = check_post_flairs(titles, flair_texts)

  for i in range(len(titles)):
    print('Post', i)
    print('Flair:', flair_texts[i])
    print('Title:', titles[i])
    print('Content:', "{:.50}".format(split_content(content, flair_texts[i])[i+1]), '...') # The i+1 is there because of the first header being a letter for the wiki index