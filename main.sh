#!/bin/bash

# Install the required libraries
pip install -r requirements.txt
echo "Installed required libraries"

# Run the main script
python3 scripts/reddit_wiki_bot.py