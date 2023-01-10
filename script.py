import praw
import os

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
user_agent = os.environ.get('USER_AGENT')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

reddit = praw.Reddit(
  client_id='client_id',
  user_agent='user_agent',
  client_secret='client_secret',
  username='username',
  password='password'
)