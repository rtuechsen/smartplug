
export DJANGO_PIPELINE=production

sudo systemctl stop nginx



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

# python3 ./manage.py collectstatic --noinput

cd ..

# http server

sudo systemctl start nginx

cd backend
gunicorn --bind 127.0.0.1:8000 src.wsgi

sudo systemctl restart gunicorn

sudo systemctl reload nginx

cd ..

# sudo systemctl start nginx -c /path/to/your/project/nginx.conf