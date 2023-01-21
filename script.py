import praw
import os
import sys
import re
import time
import csv
import pandas as pd
import hashlib
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'

second_delay = 5

fractional_delay = second_delay/100


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
    wiki_links = re.findall(
        "\* \[[A-Z] ?-? ?[A-Z]?\]\(https:\/\/www\.reddit\.com\/r\/NewToReddit\/wiki\/encyclopaedia-redditica\/[a-z]+-\d\)", wiki_page.content_md, re.MULTILINE)
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

    # Iterate through the lines
    for line in content.splitlines():
        # If the line is a title
        if re.match(title_pattern, line):
            # Get the index of the next line
            nextIndex = content.splitlines().index(line)+1
            # Get the next line
            nextLine = content.splitlines()[nextIndex]
            # If the next line is a flair
            if re.match(flair_pattern, nextLine):
                # Add the title to the titles list
                titles.append(re.findall(title_pattern, line))
                # Add the flair to the flairs list
                flairs.append(re.findall(flair_pattern, nextLine))
                # Create a variable to store the post
                post = ''
                # Iterate through the lines after the flair
                for i in range(nextIndex+1, len(content.splitlines())):
                    # If the line is a title
                    if re.match(title_pattern, content.splitlines()[i]):
                        # Break the loop
                        break
                    # Add the line to the post
                    post += content.splitlines()[i] + '\n'
                # Add the post to the posts list
                posts.append(post)
            # If the next line is not a flair
            else:
                # Add the title to the titles list
                titles.append(re.findall(title_pattern, line))
                # Add the missing flair to the flairs list
                flairs.append('::Missing flair::')
                # Create a variable to store the post
                post = ''
                # Iterate through the lines after the title
                for i in range(nextIndex, len(content.splitlines())):
                    # If the line is a title
                    if re.match(title_pattern, content.splitlines()[i]):
                        # Break the loop
                        break
                    # Add the line to the post
                    post += content.splitlines()[i] + '\n'
                # Add the post to the posts list
                posts.append(post)

    titles = [str(x).replace('[', '').replace(']', '').replace(
        '#', '').replace("'", '') for x in titles]  # Format the titles
    # Remove the whitespace
    titles = [title.strip() for title in titles]
    flairs = [str(x).replace('[', '').replace(']', '').replace(
        ':', '').replace("'", '') for x in flairs]  # Format the flairs
    # Remove the first newline
    posts = [post[1:] if post.startswith('\n') else post for post in posts]
    # Remove the horizontal rule
    posts = [post.replace('---', '') for post in posts]
    # Downgrades the headers
    posts = [post.replace('##', '#') for post in posts]
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
    # get the existing flairs in the subreddit
    existing_flairs = get_subreddit_link_flairs(sub)
    # remove duplicate entries from the list of flairs
    unique_flairs = set(flairs)
    for flair in unique_flairs:
        if flair not in existing_flairs:
            reddit.subreddit(sub).flair.link_templates.add(
                flair, css_class=flair)
            print(f"Flair {flair} created.")


def check_duplicates(titles, flairs, posts):
    # This function checks for duplicate posts using the titles and submission
    # IDs fetched from the CSV post_info.csv. The function returns a list of
    # titles that are not duplicates and can be posted.

    unique_titles = titles.copy()
    unique_flairs = flairs.copy()
    unique_posts = posts.copy()
    with open('post_info.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in unique_titles:
                removal_index = unique_titles.index(row[0])
                unique_titles.remove(row[0])
                unique_flairs.pop(removal_index)
                unique_posts.pop(removal_index)
    total_time = len(unique_titles) * second_delay
    if len(unique_titles) == 0:
        print("No new posts to be created.")
    else:
        print(f"{len(unique_titles)} post to be created in ~{total_time} seconds.")
    return unique_titles, unique_flairs, unique_posts

def check_updates(wiki_posts):
    # This function checks for updates to the wiki posts. The function returns a
    # list of post IDs and titles where the wiki entries have been updated.
    # Those post IDs are later used to update the relevant posts and the titles
    # to find the relevant post entries.

    wiki_hashes = []
    for i in range(len(wiki_posts)):
        wiki_hashes.append(hashlib.sha256(wiki_posts[i].strip().encode('utf-8')).hexdigest())

    updated_ids = []

    df = pd.read_csv('post_info.csv')
    current_hashes = df['Current Hash'].tolist()
    post_ids = df['ID'].tolist()

    for i in range(len(current_hashes)):
        if current_hashes[i] not in wiki_hashes[i]:
            updated_ids.append(post_ids[i])
    
    if len(updated_ids) == 0:
        print("No posts to be updated.")
    else:
        print(f"{len(updated_ids)} posts to be updated. IDs: {post_ids}")
    
    return updated_ids


def create_post_info(titles, flairs, wiki_hashes, ids):
    # This function creates a CSV file with the titles, flairs, and contents
    # of the posts that were created. The CSV file is used to circumvent the
    # limitation of the Reddit search API that cannot return literal matches.
    CSV_HEADER = 'Title,Flair,Current Hash,ID'

    # Create the CSV file if it doesn't exist yet
    if not os.path.exists('post_info.csv'):
        with open('post_info.csv', 'w') as file:
            file.write(CSV_HEADER + '\n')
    
    with open('post_info.csv', 'a') as file:
        for i in range(len(titles)):
            file.write(titles[i] + ',' + flairs[i] + ',' + wiki_hashes[i] + ',' + ids[i] + '\n')


def hash_content(post_content):
    # This function hashes the content of the posts to be created
    # and stores it in a csv file. The hashes are used to check
    # if edits to the wiki page have been made.
    post_hashes = []

    for i in range(len(post_content)):
        post_hashes.append(hashlib.sha256(
            post_content[i].strip().encode('utf-8')).hexdigest())

    return post_hashes


def create_posts(reddit, sub_name, posts, titles, flairs):
    post_titles = []
    post_flairs = []
    post_contents = []
    ids = []
    for i in range(len(posts)):
        subreddit = reddit.subreddit(sub_name)
        submission = subreddit.submit(titles[i], selftext=posts[i])
        choices = submission.flair.choices()
        choices_dictionary = {
            choice['flair_text']: choice['flair_template_id'] for choice in choices}

        submission.flair.select(choices_dictionary[flairs[i]])
        ids.append(submission.id)
        post_titles.append(titles[i])
        post_flairs.append(flairs[i])
        post_contents.append(posts[i])
        print(f"Post {i+1} created. Title: {titles[i]}, Flair: {flairs[i]}")
        time.sleep(second_delay)

    return ids, post_titles, post_flairs, post_contents


if __name__ == '__main__':
    fetch_env()
    reddit = reddit_login()

    print('Logged in as:', reddit.user.me())

    wiki_content = get_wiki_page('2', reddit)

    with open('2.txt', 'r') as infile:
        content = infile.read()
        # The wiki_posts here refers to the content of the wiki sections
        wiki_posts, titles, flairs = get_post_sections(content)
        with open('wiki_posts.txt', 'w') as outfile:
            for i in range(len(wiki_posts)):
                outfile.write('Title: ' + titles[i] + '\n')
                outfile.write('Flair: ' + flairs[i] + '\n')
                outfile.write('Content: ' + wiki_posts[i])

    create_missing_flairs(sub_name, flairs)

    new_titles, new_flairs, new_posts = check_duplicates(titles, flairs, wiki_posts)

    ids, post_titles, post_flairs, post_contents = create_posts(reddit, sub_name, new_posts, new_titles, new_flairs)

    current_hashes = hash_content(post_contents)

    create_post_info(post_titles, post_flairs, current_hashes, ids)

    print('Post info updated.')

    posts_to_update = check_updates(wiki_posts)