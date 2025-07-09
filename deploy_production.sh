
export DJANGO_PIPELINE=production

sudo systemctl stop nginx

sudo rm -r /etc/nginx/nginx.conf
sudo cp ./nginx.conf /etc/nginx/nginx.conf

sudo rm -r /etc/mosquitto/mosquitto.conf
sudo cp ./mosquitto.conf /etc/mosquitto/mosquitto.conf

sudo systemctl restart mosquitto

sudo rm -r /etc/systemd/system/gunicorn.service
sudo cp ./gunicorn.service /etc/systemd/system/gunicorn.service

sudo systemctl enable gunicorn

# frontend

cd frontend

npm run build

sudo rm -r /var/www/html/*
sudo cp -r -p ./dist/* /var/www/html/

cd ..

# backend

cd backend

source django-env/bin/activate

printf "\n\n\x1B[33mStarting migration.\x1B[0m\n\n\n"

sudo -E env PATH="$PATH" python manage.py clearsessions

sudo -E env PATH="$PATH" python manage.py makemigrations

sudo -E env PATH="$PATH" python manage.py migrate

printf "\n\n\x1B[33mMigration finished.\x1B[0m\n\n\n"

# TODO: dont run pylint on server start
# pylint --recursive=y smartplug_app

cd ..

# http server

cd backend

sudo systemctl daemon-reload

sudo systemctl restart nginx

sudo systemctl restart gunicorn

sudo systemctl reload nginx

cd ..

