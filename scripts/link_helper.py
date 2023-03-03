# Very similar to flair_helper.py, but this script gets the link of the
# individual posts instead of their flairs.

import re
import numpy as np
import csv
import pandas as pd

def get_title_ids():

    df = pd.read_csv(f'../post_infos/post_info.csv')
    post_titles = df['Title'].tolist()
    post_ids = df['ID'].tolist()

    post_urls = []

    for i in range(len(post_ids)):
        post_urls.append(f'https://redd.it/{post_ids[i]}/')

    # Append the title and URL into a CSV file
    with open('../post_infos/post_urls.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        CSV_HEADER = ['Title', 'URL']
        writer.writerow(CSV_HEADER)
        for i in range(len(post_titles)):
            writer.writerow([post_titles[i], post_urls[i]])


if __name__ == '__main__':
    get_title_ids()

