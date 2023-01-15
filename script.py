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

def get_post_sections(content):
  # This function iterates through the wiki content and splits up the wiki into
  # sections for later posting. Each post starts with a title (#Header)
  # and a flair (::Flair::). This function uses RegEx and requires the re
  # module.
  title_pattern = "^#[^#].*"
  flair_pattern = ":+[a-zA-Z]* ?[a-zA-Z]*:+"

  titles = []
  flairs = []
  posts = []

  for line in content.splitlines():
    if re.match(title_pattern, line):
      nextIndex = content.splitlines().index(line)+1
      nextLine = content.splitlines()[nextIndex]
      if re.match(flair_pattern, nextLine):
        titles.append(re.findall(title_pattern, line))
        flairs.append(re.findall(flair_pattern, nextLine))
        post = ''
        for i in range(nextIndex+1, len(content.splitlines())):
          if re.match(title_pattern, content.splitlines()[i]):
            break
          post += content.splitlines()[i] + '\n'
        posts.append(post)
      else:
        titles.append(re.findall(title_pattern, line))
        flairs.append('::Missing flair::')
        post = ''
        for i in range(nextIndex, len(content.splitlines())):
          if re.match(title_pattern, content.splitlines()[i]):
            break
          post += content.splitlines()[i] + '\n'
        posts.append(post)

  titles = [str(x).replace('[', '').replace(']', '').replace('#', '').replace("'", '') for x in titles]
  flairs = [str(x).replace('[', '').replace(']', '').replace(':', '').replace("'", '') for x in flairs]
  posts = [post[1:] if post.startswith('\n') else post for post in posts]
  posts = [post.replace('---', '') for post in posts]
  posts = [re.sub('^(#+)', lambda match: match.group(1)[:-1], post) for post in posts]

  return posts, titles, flairs

if __name__ == '__main__':
  fetch_env()
  # reddit = reddit_login()

  # print('Logged in as:', reddit.user.me())

  # online_content = get_wiki_page('2', reddit)

  # open the 2.txt file and read the content
  with open('2.txt', 'r') as infile:
    content = infile.read()
    posts, titles, flairs = get_post_sections(content)
    with open('posts.txt', 'w') as outfile:
      for i in range(len(posts)):
        outfile.write('Title: ' + titles[i] + '\n')
        outfile.write('Flair: ' + flairs[i] + '\n')
        outfile.write('Content: ' + posts[i])
        outfile.write('')