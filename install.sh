
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

pip install -r ./requirements.txt

cd ..

# frontend

cd frontend

sudo apt -y install nodejs

npm install

cd ..


