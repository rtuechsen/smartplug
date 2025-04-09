
export DJANGO_PIPELINE=production

sudo systemctl stop nginx

sudo systemctl start nginx

# frontend

cd frontend

npm run build

cd ..


# backend

python3 ./backend/manage.py makemigrations

python3 ./backend/manage.py migrate

python3 ./backend/manage.py collectstatic --noinput

cd backend
gunicorn --bind 127.0.0.1:8000 src.wsgi

sudo systemctl restart gunicorn

sudo systemctl reload nginx

cd ..

# sudo systemctl start nginx -c /path/to/your/project/nginx.conf