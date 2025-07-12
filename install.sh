
UBUNTU_VERSION=$(lsb_release -a)

if [[ $UBUNTU_VERSION != *"24.04"* ]]; then
	printf "\nERROR: wrong version of ubuntu:\n$UBUNTU_VERSION\n\n"
	exit 1
else
	printf "\nSUCCESS: correct version of ubuntu:\n$UBUNTU_VERSION\n\n"
fi

sudo apt update
sudo apt -y upgrade

# nginx

sudo apt -y install nginx

# backend

cd backend

sudo apt -y install python3-venv
python3 -m venv django-env
source django-env/bin/activate

sudo apt -y install python3-pip

python -m pip install -r ./requirements.txt

## LDAP

sudo apt install -y libsasl2-dev python3-dev libldap2-dev libssl-dev ldap-utils

## linter

sudo apt install -y pylint

## mosquitto

sudo apt install -y mosquitto mosquitto-clients
sudo systemctl stop mosquitto

# set mosquitto password

sudo mosquitto_passwd -c /etc/mosquitto/passwd mqttuser

# TODO: call generate_secrets.py to generate secrets for django for development and production

cd ..

# frontend

cd frontend

sudo apt -y install npm
sudo apt -y install nodejs

npm install

npm audit fix

cd ..

# ssl key

if ! [ -d /etc/nginx/ssl/ ]; then
	sudo mkdir /etc/nginx/ssl/
fi

sudo openssl genpkey -algorithm RSA -out /etc/nginx/ssl/selfsigned.key

sudo openssl req -new -x509 \
  -key /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -days 365 \
  -subj "/C=DE/CN=localhost"

# doxygen

sudo apt -y install doxygen

sudo bash change_permissions.sh

## logrotate

if ! [ -f /etc/logrotate.d/smartplug_app ]; then
	sudo rm /etc/logrotate.d/smartplug_app
fi
sudo cp ./smartplug_app /etc/logrotate.d/smartplug_app
