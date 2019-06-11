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
echo -n "Generate config.py? [y/n]: "
read generate_config
if [[ ${generate_config,,} == "y" || ${generate_config,,} == "yes" ]]; then
    echo -n "Enter telegram API token and press [ENTER]: "
    read token
    echo -n "Enter username to access https://rutracker.org and press [ENTER]: "
    read rutracker_username
    echo -n "Enter password for ${rutracker_username} and press [ENTER]: "
    read rutracker_password
    cat > ./app/config.py << EOL
token = "${token}"
database_name = "/app/rutracker_notifier.db"
rutracker_login = "${rutracker_username}"
rutracker_password = "${rutracker_password}"
EOL
fi

echo -n "Enter path to DB file with data if you have any. To use default (./app/rutracker_notifier.db) just press [ENTER]: "
read user_db_path
if [[ -n $user_db_path ]]; then
    rm -f ./app/rutracker_notifier.db
    cp $user_db_path ./app/rutracker_notifier.db
fi
# Build image
docker build -t rutracker_notifier_image .

# Run container from image
docker run -dit --restart unless-stopped --name=rutracker_notifier -v rutracker_notifier_bot_app:/app rutracker_notifier_image
