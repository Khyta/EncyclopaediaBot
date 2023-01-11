import praw
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
  os.getenv('CLIENT_ID')
  os.getenv('CLIENT_SECRET')
  os.getenv('USER_AGENT')
  os.getenv('REDDIT_USERNAME')
  os.getenv('PASSWORD')
except KeyError:
  print('[error]: Missing environment variable(s)')
  sys.exit(1)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')
username = os.getenv('REDDIT_USERNAME')
password = os.getenv('PASSWORD')

reddit = praw.Reddit(
  client_id=client_id,
  user_agent=user_agent,
  client_secret=client_secret,
  username=username,
  password=password
)

print(reddit.user.me())