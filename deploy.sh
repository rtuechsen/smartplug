
export DJANGO_PIPELINE=production

sudo systemctl stop nginx

sudo rm -r /etc/nginx/nginx.conf
sudo cp ./nginx.conf /etc/nginx/nginx.conf

# frontend

cd frontend

npm run build

sudo rm -r /var/www/html/*
sudo cp -r -p ./dist/* /var/www/html/

cd ..

# backend

cd backend

python3 ./manage.py makemigrations

python3 ./manage.py migrate

cd ..

# http server

sudo systemctl start nginx

cd backend
gunicorn --bind 127.0.0.1:8000 shelly_dirigent.wsgi

sudo systemctl restart gunicorn

sudo systemctl reload nginx

cd ..
