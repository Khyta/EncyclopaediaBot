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

# Check if an argument is passed to this script
if [ -z "$1" ]; then
  # No argument passed, run the main script without any argument
  python3 scripts/reddit_wiki_bot.py 
else
  # Argument passed, run the main script with the argument passed to this script
  python3 scripts/reddit_wiki_bot.py $1 
fi