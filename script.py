import praw
import os
import sys
import re
import time
import csv
import glob
import pandas as pd
import numpy as np
import hashlib
import logging as log
import datetime
from dotenv import load_dotenv

load_dotenv()

sub_name = 'EncyclopaediaOfReddit'

minute_delay = 5

second_delay = 5

fractional_delay = second_delay/100

now = datetime.datetime.now()
filename = now.strftime("%d-%m-%Y %H_00") + '.log'

logger = log.getLogger()
logger.setLevel(log.INFO)
handler = log.FileHandler(filename)
handler.setLevel(log.INFO)
formatter = log.Formatter('%(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
        log.error('Could not find environment variables.')
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

    titles = list(np.concatenate(titles).flat)  # Flatten the titles list
    titles = [title.strip() for title in titles]
    titles = [str(x).replace('#', '', 1) for x in titles]  # Format the titles
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
            log.info(f"Flair '{flair}' created.")


def check_additions(wiki_page_id, titles, flairs, posts):
    # This function checks for duplicate posts using the titles and submission
    # IDs fetched from the CSV post_info.csv. The function returns a list of
    # titles that are not duplicates and can be posted.

    unique_titles = titles.copy()
    unique_flairs = flairs.copy()
    unique_posts = posts.copy()

    CSV_HEADER = 'Title,Flair,Current Hash,ID'

    if not os.path.exists(f'post_info_{wiki_page_id}.csv'):
        with open(f'post_info_{wiki_page_id}.csv', 'w') as file:
            file.write(CSV_HEADER + '\n')

    with open(f'post_info_{wiki_page_id}.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] in unique_titles:
                removal_index = unique_titles.index(row[0])
                unique_titles.remove(row[0])
                unique_flairs.pop(removal_index)
                unique_posts.pop(removal_index)
    total_time = len(unique_titles) * second_delay
    if len(unique_titles) == 0:
        log.info(f"No new posts to be created for wiki page {wiki_page_id}.")
    else:
        log.info(f"{len(unique_titles)} post to be created from wiki page {wiki_page_id}.")
    return unique_titles, unique_flairs, unique_posts


def check_updates(wiki_page_id, wiki_posts, wiki_flairs, wiki_titles):
    # This function checks for updates to the wiki posts. The function returns a
    # list of post IDs and titles where the wiki entries have been updated.
    # Those post IDs are later used to update the relevant posts and the titles
    # to find the relevant post entries.

    post_updates = False
    flair_updates = False

    post_hashes = []
    post_hashes = hash_content(wiki_posts)

    flair_hashes = []

    combined_wiki_flair_and_wiki_title = [wiki_flairs[i].strip() + wiki_titles[i].strip()
                            for i in range(len(wiki_titles))]

    flair_hashes = hash_content(combined_wiki_flair_and_wiki_title)

    updated_ids = []

    df = pd.read_csv(f'post_info_{wiki_page_id}.csv')
    current_post_hashes = df['Current Post Hash'].tolist()
    current_flair_hashes = df['Current Flair Hash'].tolist()
    current_titles = df['Title'].tolist()
    post_ids = df['ID'].tolist()

    for i in range(len(current_post_hashes)):
        if current_post_hashes[i] not in post_hashes:
            updated_ids.append(post_ids[i])
            post_updates = True

    for i in range(len(current_flair_hashes)):
        if current_flair_hashes[i] not in flair_hashes:
            updated_ids.append(post_ids[i])                                      
            flair_updates = True                                                 


    if len(updated_ids) == 0:
        log.info(f"No posts or flairs to be updated from wiki page {wiki_page_id}.")
    elif post_updates:
        log.info(f"{len(updated_ids)} posts to be updated. IDs: {updated_ids}")
    elif flair_updates:
        log.info(f"{len(updated_ids)} flairs to be updated. IDs: {updated_ids}")

    return updated_ids, post_updates, flair_updates


def create_post_info(wiki_page_id, titles, flairs, wiki_hashes, flair_hashes, ids):
    # This function creates a CSV file with the titles, flairs, and contents
    # of the posts that were created. The CSV file is used to circumvent the
    # limitation of the Reddit search API that cannot return literal matches.
    CSV_HEADER = 'Title,Flair,Current Post Hash, Current Flair Hash, ID'

    # Create the CSV file if it doesn't exist yet
    if not os.path.exists(f'post_info_{wiki_page_id}.csv'):
        with open(f'post_info_{wiki_page_id}.csv', 'w') as file:
            file.write(CSV_HEADER + '\n')
    if len(titles) != 0:
        with open(f'post_info_{wiki_page_id}.csv', 'a') as file:
            writer = csv.writer(file)
            for i in range(len(titles)):
                writer.writerow([titles[i], flairs[i],
                             wiki_hashes[i], flair_hashes[i], ids[i]])
        log.info('Post info updated.')


def hash_content(content):
    # This function hashes the content of the posts to be created
    # and stores it in a csv file. The hashes are used to check
    # if edits to the wiki page have been made.
    content_hashes = []

    for i in range(len(content)):
        content_hashes.append(hashlib.sha256(
            content[i].strip().encode('utf-8')).hexdigest())

    return content_hashes


def create_posts(reddit, sub_name, posts, titles, flairs):
    post_titles = []
    post_flairs = []
    post_contents = []
    ids = []
    post_created = False
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
        log.info(f"'{titles[i]}' created. Flair: '{flairs[i]}'")
        post_created = True
        # time.sleep(second_delay)

    return ids, post_titles, post_flairs, post_contents, post_created

def update_posts(wiki_page_id, update_ids):

    # This function updates the posts that have been edited in the wiki page.
    # The function takes the post IDs as input and updates the posts with the
    # new content.
    update_titles = []
    with open(f'post_info_{wiki_page_id}.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[4] in update_ids:
                update_titles.append(row[0])

    # log.info(f"Updating {len(update_titles)} posts: {update_titles}.")

    with open(f'{wiki_page_id}.txt', 'r') as infile:
        content = infile.read()
        wiki_posts, titles, flairs = get_post_sections(content)

    for i in range(len(update_titles)):
        post = reddit.submission(id=update_ids[i])
        reddit.validate_on_submit = True
        post.edit(wiki_posts[titles.index(update_titles[i])])
        log.info(f"'{update_titles[i]}' updated.")
        # time.sleep(second_delay)

    wiki_hashes = hash_content(wiki_posts)

    # Update hashes in the CSV file according to the ID of the updated post
    df = pd.read_csv(f'post_info_{wiki_page_id}.csv')
    for i in range(len(update_titles)):
        row_to_update = df.loc[df['ID'] == update_ids[i]].index[0]
        df.at[row_to_update, 'Current Post Hash'] = wiki_hashes[titles.index(update_titles[i])]
    df.to_csv(f'post_info_{wiki_page_id}.csv', index=False)

def update_post_flairs(wiki_page_id, update_ids):
    # This function updates the post flairs based on wiki page edits and the
    # flair hash in the CSV file. The flair hash was made unique by combining
    # the post title and the flair text. This was done to make looking for
    # unique hashes easier.
    update_titles = []
    with open(f'post_info_{wiki_page_id}.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[4] in update_ids:
                update_titles.append(row[0])

    log.info(f"Updating {len(update_ids)} post flairs: {update_titles}.")
    with open(f'{wiki_page_id}.txt', 'r') as infile:
        content = infile.read()
        wiki_posts, titles, flairs = get_post_sections(content)

    for i in range(len(update_ids)):
        post = reddit.submission(id=update_ids[i])
        choices = post.flair.choices()
        choices_dictionary = {
            choice['flair_text']: choice['flair_template_id'] for choice in choices}
        post.flair.select(choices_dictionary[flairs[titles.index(update_titles[i])]])
        log.info(f"Post flair {i+1} updated. Title: {update_titles[i]}, Flair: {flairs[titles.index(update_titles[i])]}")
        # time.sleep(second_delay)

    combined_flairs_and_titles = [flairs[i] + titles[i] for i in range(len(flairs))]
    flair_hashes = hash_content(combined_flairs_and_titles)

    # Update hashes in the CSV file according to the ID of the updated post
    df = pd.read_csv(f'post_info_{wiki_page_id}.csv')
    for i in range(len(update_ids)):
        row_to_update = df.loc[df['ID'] == update_ids[i]].index[0]
        df.at[row_to_update, 'Current Flair Hash'] = flair_hashes[titles.index(update_titles[i])]
    df.to_csv(f'post_info_{wiki_page_id}.csv', index=False)

def delete_posts(wiki_page_id, wiki_titles):
    # This function deletes the posts that have been deleted from the wiki page.
    # The function takes in the wiki titles as input and deletes the posts where
    # the titles are no longer in the post_info.csv file.
    df = pd.read_csv(f'post_info_{wiki_page_id}.csv')
    post_titles = df['Title'].tolist()
    post_ids = df['ID'].tolist()

    for i in range(len(post_titles)):
        if post_titles[i] not in wiki_titles:
            post = reddit.submission(id=post_ids[i])
            post.delete()
            log.info(f"Post '{post_titles[i]}' deleted.")
            # time.sleep(second_delay)

    # Remove the deleted posts from the CSV file
    for i in range(len(post_titles)):
        if post_titles[i] not in wiki_titles:
            row_to_delete = df.loc[df['Title'] == post_titles[i]].index[0]
            df.drop(row_to_delete, inplace=True)
    df.to_csv(f'post_info_{wiki_page_id}.csv', index=False)

def csv_to_dict():
    title_id_dict = {}
    with open(f'post_info.csv', 'r') as file:
        reader = csv.DictReader(file, fieldnames=['Title', 'Flair', 'Current Post Hash', 'Current Flair Hash', 'ID'])
        next(reader) # skip header row
        for row in reader:
            title_id_dict[row['Title']] = row['ID']
    # log.info(f"CSV file converted to dictionary. {title_id_dict}")
    return title_id_dict

# IDEA:
# 1. Check each post using the ID in the CSV file
# 2. Look for links that resemble wiki links in each post
# 3. Check for to what wiki page the link points to
# 4. Convert the wiki link to a post link using the title_id_dict 

def wiki_to_post_link(reddit, title_id_dict, ids):
    df = pd.read_csv(f'post_info.csv')
    post_ids = ids.copy()
    headings = df['Title'].tolist()

    log.info(f"Converting wiki links to post links in {len(post_ids)} posts: {post_ids}.")

    for i in range(len(post_ids)):
        post = reddit.submission(id=post_ids[i])
        post_content = post.selftext
        if "https://www.reddit.com/r/EncyclopaediaOfReddit/about/wiki" not in post_content:
            log.info(f"Links in '{list(title_id_dict.keys())[list(title_id_dict.values()).index(post_ids[i])]}' already converted, skipping...")
            continue
        for heading in headings:
            converted_heading = url_encoding(heading)
            # log.info(f"Converted heading: {converted_heading}") 
            pattern = re.compile(f'\\[{heading}\\]\\(https://www.reddit.com/r/EncyclopaediaOfReddit/about/wiki/[0-9]+/#wiki_{converted_heading}\\)') # TODO This regex is not working properly. Confirmed breaks with '$' in the heading.
            post_link = f'[{heading}](https://www.reddit.com/r/EncyclopaediaOfReddit/comments/{title_id_dict[heading]}/)'
            post_content = re.sub(pattern, post_link, post_content)
            # log.info(f"Title_ID dictionary: {title_id_dict[heading]}")
        reddit.validate_on_submit = True
        try:
            post.edit(post_content)
            log.info(f"Wiki links converted for '{list(title_id_dict.keys())[list(title_id_dict.values()).index(post_ids[i])]}'")
        except Exception as e:
            log.error(f"Error updating post for '{list(title_id_dict.keys())[list(title_id_dict.values()).index(post_ids[i])]}'. Likely post has been deleted. Error: {e}")


def combine_csvs():
    # This function combines all the post_info_*.csv files into one file for the
    # wiki_to_post_link conversion to function properly for interwiki links.

    csv_files = glob.glob('post_info_*.csv')
    combined_csv = pd.concat([pd.read_csv(f) for f in csv_files])
    combined_csv.to_csv('post_info.csv', index=False)

def url_encoding(heading):
    # This function converts the heading that may contain special characters in
    # a reddit post link to a format that can be used in a wiki link. For
    # example, it will convert / to .2F. Sadly the percent encoding does not
    # work as reddit uses . instead of % for some reason.
    heading = heading.lower()
    heading = heading.replace(' ', '_')
    heading = heading.replace('/', '.2F')
    heading = heading.replace('\\', '.5C')
    heading = heading.replace('?', '.3F')
    heading = heading.replace('!', '.21')
    heading = heading.replace('“', '.201C')
    heading = heading.replace('”', '.201D')
    heading = heading.replace('"', '.22')
    heading = heading.replace("'", '.27')
    heading = heading.replace('’', '.2019')
    heading = heading.replace('`', '.60')
    heading = heading.replace('@', '.40')
    heading = heading.replace(':', '.3A')
    heading = heading.replace(';', '.3B')
    heading = heading.replace('(', '.28')
    heading = heading.replace(')', '.29')
    heading = heading.replace(',', '.2C')
    heading = heading.replace('#', '.23')
    heading = heading.replace('~', '.7E')
    heading = heading.replace('$', '.24')
    heading = heading.replace('%', '.25')
    heading = heading.replace('&', '.26amp.3B')
    heading = heading.replace('+', '.2B')
    heading = heading.replace('<', '.26lt.3B')
    heading = heading.replace('>', '.26gt.3B')
    heading = heading.replace('=', '.3D')
    heading = heading.replace('{', '.7B')
    heading = heading.replace('}', '.7D')
    heading = heading.replace('[', '.5B')
    heading = heading.replace(']', '.5D')
    heading = heading.replace('^', '.5E')
    heading = heading.replace('|', '.7C')

    return heading

def handle_wiki_page(wiki_page_id, reddit):
    wiki_content = get_wiki_page(wiki_page_id, reddit)

    with open(f'{wiki_page_id}.txt', 'r') as infile:
        content = infile.read()
        # The wiki_posts here refers to the content of the wiki sections
        wiki_posts, titles, flairs = get_post_sections(content)

    delete_posts(wiki_page_id, titles)

    create_missing_flairs(sub_name, flairs)

    new_titles, new_flairs, new_posts = check_additions(
        wiki_page_id, titles, flairs, wiki_posts)

    ids, post_titles, post_flairs, post_contents, post_created = create_posts(
        reddit, sub_name, new_posts, new_titles, new_flairs)

    current_post_hashes = hash_content(post_contents)
    combined_flair_and_title = [flairs[i].strip() + titles[i].strip()
                            for i in range(len(titles))]
    current_flair_hashes = hash_content(combined_flair_and_title)

    create_post_info(wiki_page_id, post_titles, post_flairs, current_post_hashes, current_flair_hashes, ids)

    combine_csvs()

    stuff_to_update = check_updates(wiki_page_id, wiki_posts, flairs, titles)

    if len(stuff_to_update[0]) > 0:
        title_id_dict = csv_to_dict()
        if stuff_to_update[1] == True:
            update_posts(wiki_page_id, stuff_to_update[0])
            wiki_to_post_link(reddit, title_id_dict, stuff_to_update[0])
        elif stuff_to_update[2] == True:
            update_post_flairs(wiki_page_id, stuff_to_update[0])

    if post_created == True:
        title_id_dict = csv_to_dict()
        # log.info(f'Title id {title_id_dict}')
        wiki_to_post_link(reddit, title_id_dict, ids)



if __name__ == '__main__':
    fetch_env()
    reddit = reddit_login()

    print('Logged in as:', reddit.user.me())

    # List of wiki page IDs to process
    wiki_page_ids = ['1', '2']

    t0 = time.time()
    for page_id in wiki_page_ids:
        handle_wiki_page(page_id, reddit)
    t1 = time.time()
    total = round(t1-t0, 3)

    log.info(f'Finished processing wiki pages in {total} seconds')