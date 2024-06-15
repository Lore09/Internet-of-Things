#|/bin/bash
echo 'Building python container'

docker build -t unibo-iot/python-telegram-bot .

echo 'Container built'
echo''
echo 'Import the container in k3s with the following command:'
echo 'docker save unibo-iot/python-telegram-bot:latest | sudo k3s ctr images import -'