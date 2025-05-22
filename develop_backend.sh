
export DJANGO_PIPELINE=development

sudo rm -r /etc/mosquitto/mosquitto.conf
sudo cp ./mosquitto.conf /etc/mosquitto/mosquitto.conf

sudo systemctl stop mosquitto
sudo systemctl start mosquitto

cd backend

sudo systemctl stop nginx

printf "\n\n\x1B[33mStarting migration. During migration runtime errors can occure that do not happen at normal runtime.\x1B[0m\n\n\n"

python3 manage.py makemigrations

python3 manage.py migrate

printf "\n\n\x1B[33mMigration finished. Runtime errors above can possibly be ignored if they do not show up below.\x1B[0m\n\n\n"

sudo  -E env PATH="$PATH" uvicorn smartplug_app.asgi:application


