#!/bin/bash
set -e

# Install Docker
apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install docker-ce

# Prepare config.py
echo -n "Enter telegram API token and press [ENTER]: "
read token
echo -n "Enter username to access https://rutracker.org and press [ENTER]: "
read rutracker_username
echo -n "Enter password for ${rutracker_username} and press [ENTER]: "
read rutracker_password
echo -n "Enter path to DB file with data if you have any. Otherwise just press [ENTER]: "
read db_path
sed -i "s/ENTER_TOKEN/${token}/g" ./app/config.py
sed -i "s/ENTER_rutracker_login/${rutracker_username}/g" ./app/config.py
sed -i "s/ENTER_rutracker_pass/${rutracker_password}/g" ./app/config.py
sed -i "s:rutracker_notifier.db:/mnt/rutracker_notifier.db:g" ./app/config.py

if [[ -z $db_path ]]; then
    mv ./app/rutracker_notifier.db ~/rutracker_notifier_bot_app/
else
    cp $db_path ~/rutracker_notifier_bot_app/rutracker_notifier.db
fi

# Build image
docker build -t rutracker_notifier_image .

# Run container from image
docker run -d --name=rutracker_notifier -v ~/rutracker_notifier_bot_app:/mnt rutracker_notifier_image
