import praw
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def fetch_env():
  try:
    os.getenv('CLIENT_ID')
    client_id = os.getenv('CLIENT_ID')
    os.getenv('CLIENT_SECRET')
    client_secret = os.getenv('CLIENT_SECRET')
    os.getenv('USER_AGENT')
    user_agent = os.getenv('USER_AGENT')
    os.getenv('REDDIT_USERNAME')
    username = os.getenv('REDDIT_USERNAME')
    os.getenv('PASSWORD')
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