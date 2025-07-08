
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

## logrotate

sudo cp -p ./smartplug_app /etc/logrotate.d/smartplug_app

## LDAP

sudo apt install -y libsasl2-dev python3-dev libldap2-dev libssl-dev ldap-utils

## linter

sudo apt install -y pylint

## mosquitto

sudo apt install -y mosquitto mosquitto-clients
sudo systemctl stop mosquitto

##set mosquitto Password

sudo mosquitto_passwd -c /ect/mosquitto/passwd mqttuser
sudo chmod 600 /etc/mosquitto/passwd
sudo chown mosquitto: /etc/mosquitto/passwd


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

