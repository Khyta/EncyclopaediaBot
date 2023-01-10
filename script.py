import praw
import os

client_id = os.environ.get('CLIENT_ID')

reddit = praw.Reddit(
  client_id='client_id',
  user_agent='user_agent',
  client_secret='client_secret',
  username='username',
  password='password'
)

print(reddit.user.me())