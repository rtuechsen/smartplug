
export DJANGO_PIPELINE=production

source backend/django-env/bin/activate

sudo systemctl stop smartplug

sudo rm -r /etc/nginx/nginx.conf
sudo cp ./nginx.conf /etc/nginx/nginx.conf

sudo rm -r /etc/mosquitto/mosquitto.conf
sudo cp ./mosquitto.conf /etc/mosquitto/mosquitto.conf

sudo systemctl restart mosquitto

# frontend

cd frontend

npm run build

sudo rm -r /var/www/html/*
sudo cp -r -p ./dist/* /var/www/html/

cd ..

# backend

cd backend

printf "\n\n\x1B[33mStarting migration.\x1B[0m\n\n\n"

sudo -E env PATH="$PATH" python manage.py clearsessions

sudo -E env PATH="$PATH" python manage.py makemigrations

sudo -E env PATH="$PATH" python manage.py migrate

printf "\n\n\x1B[33mMigration finished.\x1B[0m\n\n\n"

cd ..

if [ -f /etc/systemd/system/smartplug.service ]; then
	sudo rm -r /etc/systemd/system/smartplug.service
fi

sudo cp ./smartplug.service /etc/systemd/system/smartplug.service

sudo systemctl daemon-reload

# http server

# cd backend

# sudo systemctl start nginx

# TODO: adjust the number of workers or mention it in the admin documentation
# sudo -E env PATH="$PATH" gunicorn --bind 127.0.0.1:8000 smartplug_app.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 1 --graceful-timeout 0

# sudo systemctl restart gunicorn

# sudo systemctl reload nginx

# cd ..
