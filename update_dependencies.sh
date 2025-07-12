
sudo apt update
sudo apt -y upgrade

cd backend

source django-env/bin/activate

python -m pip install -r ./requirements.txt

cd ..

cd frontend

npm install

npm audit fix

cd ..

