#!/bin/bash

# Check if the required libraries are already installed
if pip freeze | grep -Fq -f requirements.txt; then
  echo "Required libraries are already installed"
else
  # Install the required libraries
  pip install -r requirements.txt
  echo "Installed required libraries"
fi

# Run the main script
python3 scripts/reddit_wiki_bot.py