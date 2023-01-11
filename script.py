import praw
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def fetch_env():
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

client_id = fetch_env()[0]
client_secret = fetch_env()[1]
user_agent = fetch_env()[2]
username = fetch_env()[3]
password = fetch_env()[4]

reddit = praw.Reddit(
  client_id=client_id,
  user_agent=user_agent,
  client_secret=client_secret,
  username=username,
  password=password
)

print('Logged in as:', reddit.user.me())