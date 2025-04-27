
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

printf "\n\n\x1B[33mStarting migration. During migration runtime errors can occure that do not happen at normal runtime.\x1B[0m\n\n\n"

python3 ./manage.py makemigrations

python3 ./manage.py migrate

printf "\n\n\x1B[33mMigration finished. Runtime errors above can possibly be ignored if they do not show up below.\x1B[0m\n\n\n"

cd ..

# http server

sudo systemctl start nginx

cd backend

sudo -E env PATH="$PATH" gunicorn --bind 127.0.0.1:8000 shelly_dirigent.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 1

sudo systemctl restart gunicorn

sudo systemctl reload nginx

cd ..
