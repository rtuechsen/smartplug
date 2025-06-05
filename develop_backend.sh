
export DJANGO_PIPELINE=development

sudo rm -r /etc/mosquitto/mosquitto.conf
sudo cp ./mosquitto.conf /etc/mosquitto/mosquitto.conf

sudo systemctl stop mosquitto
sudo systemctl start mosquitto

cd backend

sudo systemctl stop nginx

printf "\n\n\x1B[33mStarting migration.\x1B[0m\n\n\n"

sudo -E env PATH="$PATH" python manage.py clearsessions

sudo -E env PATH="$PATH" python manage.py makemigrations

sudo -E env PATH="$PATH" python manage.py migrate

printf "\n\n\x1B[33mMigration finished.\x1B[0m\n\n\n"

sudo -E env PATH="$PATH" uvicorn smartplug_app.asgi:application


