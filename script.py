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
  # This function gets the contents of a wiki page and saves it to a text file.
  sub = reddit.subreddit(sub_name)
  wiki_page = sub.wiki[page]
  with open(page+'.txt', 'w') as file:
    file.write(wiki_page.content_md)
  return wiki_page.content_md

def split_content(content, titles, flairs):
  # This function splits the wiki content up at each title and then
  # removes the flair and header used for the submission itself inside the wiki
  # content.
  contents = re.split(r"#[a-zA-Z]* ?[a-zA-Z]*\n", content)
  contents = [content.replace('::'+flairs+'::', '') for content in contents]
  contents = [content.replace('#'+titles, '') for content in contents]
  return contents

def get_post_sections(content):
  # This function iterates through the wiki content and splits up the wiki into
  # sections for later posting. Each post starts with a title (#Header)
  # and a flair (::Flair::). This function uses RegEx and requires the re
  # module. Regex expression to match the start of the sections: "#[a-zA-Z]+ ?[a-zA-Z]+\n::[a-zA-Z]+ ?[a-zA-Z]+::"
  post_with_flair = "#[a-zA-Z]* ?[a-zA-Z]*\n::[a-zA-Z]* ?[a-zA-Z]*::"
  post_without_flair = "#[a-zA-Z]* ?[a-zA-Z]*\n"
  title_pattern = "#[a-zA-Z]* ?[a-zA-Z]*"
  flair_pattern = "::[a-zA-Z]* ?[a-zA-Z]*::"
  posts_with_flair = []
  titles = []
  flairs = []
  for post in re.finditer(post_with_flair, content):
    titles.append(re.findall(title_pattern, post.group())[0].replace('#', ''))
    flairs.append(re.findall(flair_pattern, post.group())[0].replace('::', ''))
    split_content = content.split(post.group())
  return posts_with_flair, titles, flairs

if __name__ == '__main__':
  fetch_env()
  reddit = reddit_login()

  print('Logged in as:', reddit.user.me())

  content = get_wiki_page('2', reddit)
  posts, titles, flairs = get_post_sections(content)
  print(titles)