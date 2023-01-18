import praw
import os
import sys
import re
import time
import csv
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

  for line in content.splitlines():                                                                   # Iterate through the lines
    if re.match(title_pattern, line):                                                                 # If the line is a title
      nextIndex = content.splitlines().index(line)+1                                                  # Get the index of the next line
      nextLine = content.splitlines()[nextIndex]                                                      # Get the next line
      if re.match(flair_pattern, nextLine):                                                           # If the next line is a flair
        titles.append(re.findall(title_pattern, line))                                                # Add the title to the titles list
        flairs.append(re.findall(flair_pattern, nextLine))                                            # Add the flair to the flairs list
        post = ''                                                                                     # Create a variable to store the post
        for i in range(nextIndex+1, len(content.splitlines())):                                       # Iterate through the lines after the flair
          if re.match(title_pattern, content.splitlines()[i]):                                        # If the line is a title
            break                                                                                     # Break the loop
          post += content.splitlines()[i] + '\n'                                                      # Add the line to the post
        posts.append(post)                                                                            # Add the post to the posts list
      else:                                                                                           # If the next line is not a flair
        titles.append(re.findall(title_pattern, line))                                                # Add the title to the titles list
        flairs.append('::Missing flair::')                                                            # Add the missing flair to the flairs list
        post = ''                                                                                     # Create a variable to store the post
        for i in range(nextIndex, len(content.splitlines())):                                         # Iterate through the lines after the title
          if re.match(title_pattern, content.splitlines()[i]):                                        # If the line is a title
            break                                                                                     # Break the loop
          post += content.splitlines()[i] + '\n'                                                      # Add the line to the post
        posts.append(post)                                                                            # Add the post to the posts list

  titles = [str(x).replace('[', '').replace(']', '').replace('#', '').replace("'", '') for x in titles] # Format the titles
  titles = [title.strip() for title in titles]                                                          # Remove the whitespace
  flairs = [str(x).replace('[', '').replace(']', '').replace(':', '').replace("'", '') for x in flairs] # Format the flairs
  posts = [post[1:] if post.startswith('\n') else post for post in posts]                               # Remove the first newline
  posts = [post.replace('---', '') for post in posts]                                                   # Remove the horizontal rule
  posts = [post.replace('##', '#') for post in posts]                                                   # Downgrades the headers
  posts = [post.replace('###', '##') for post in posts]
  posts = [post.replace('####', '###') for post in posts]
  posts = [post.replace('#####', '####') for post in posts]
  posts = [post.replace('######', '#####') for post in posts]

  return posts, titles, flairs

def get_subreddit_link_flairs(sub):
    flairs = []
    for template in reddit.subreddit(sub).flair.link_templates:
        flairs.append(template["text"])
    return flairs

def create_missing_flairs(sub, flairs):
    existing_flairs = get_subreddit_link_flairs(sub) # get the existing flairs in the subreddit
    unique_flairs = set(flairs) # remove duplicate entries from the list of flairs
    for flair in unique_flairs:
      if flair not in existing_flairs:
        reddit.subreddit(sub).flair.link_templates.add(flair, css_class=flair)
        print(f"Flair {flair} created.")

def check_duplicates(sub, titles, flairs, posts):
    # This function checks for duplicate posts using the titles and submission
    # IDs fetched from the subreddit. The existing titles are stored in a .csv
    # with their corresponding submission IDs. The function returns a list of
    # titles that are not duplicates.
    existing_titles = []
    existing_ids = []

    CSV_HEADER = 'Title, ID'

    for submission in sub.new(limit=None):
        existing_titles.append(submission.title)
        existing_ids.append(submission.id)


    with open('existing_titles.csv', 'w') as file:
        file.write(CSV_HEADER + '\n')
        for i in range(len(existing_titles)):
            file.write(existing_titles[i] + ',' + existing_ids[i] + '\n')

    with open('existing_titles.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in titles:
                removal_index = titles.index(row[0])
                titles.remove(row[0])
                flairs.pop(removal_index)
                posts.pop(removal_index)
    print(f"Number of new posts to be created: {len(titles)}")
    return titles

def create_posts(reddit, sub_name, posts, titles, flairs):
  for i in range(len(titles)):
    subreddit = reddit.subreddit(sub_name)
    submission = subreddit.submit(titles[i], selftext=posts[i])
    choices = submission.flair.choices()
    choices_dictionary = {choice['flair_text']: choice['flair_template_id'] for choice in choices}
    
    submission.flair.select(choices_dictionary[flairs[i]])
    print(f"Post {i} created. Title: {titles[i]}, Flair: {flairs[i]}")
    time.sleep(5)

if __name__ == '__main__':
  fetch_env()
  reddit = reddit_login()

  print('Logged in as:', reddit.user.me())

  online_content = get_wiki_page('2', reddit)

  with open('2.txt', 'r') as infile:
    content = infile.read()
    posts, titles, flairs = get_post_sections(content)
    with open('posts.txt', 'w') as outfile:
      for i in range(len(posts)):
        outfile.write('Title: ' + titles[i] + '\n')
        outfile.write('Flair: ' + flairs[i] + '\n')
        outfile.write('Content: ' + posts[i])

  # create_missing_flairs(sub_name, flairs)
  check_duplicates(reddit.subreddit(sub_name), titles, flairs, posts)

  for i in range(len(titles)):
    print(f"Title: {titles[i]}, Flair: {flairs[i]}")
  # create_posts(reddit, sub_name, posts, titles, flairs)