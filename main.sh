#!/bin/bash

# Check if the required libraries are already installed
if pip3 freeze | grep -Fq -f requirements.txt; then
  echo "Required libraries are already installed"
else
  # Install the required libraries
  pip3 install -r requirements.txt
  echo "Installed required libraries"
fi

#Check if logs directory is present
if [ ! -d "logs" ]; then
  mkdir logs
  echo "Created logs directory"
fi

# Run the main script
python3 scripts/reddit_wiki_bot.py