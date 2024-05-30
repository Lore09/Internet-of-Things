#|/bin/bash
echo 'Building python container'

docker build -t unibo-iot/python-data-proxy-server .

echo 'Container built'
echo 'Possible environment variables:'
cat .env.template

echo''
echo 'To run docker container run: docker run -d unibo-iot/python-data-proxy-server'