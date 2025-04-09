
export DJANGO_PIPELINE=production

sudo systemctl stop nginx

python3 manage.py makemigrations

python3 manage.py migrate

python3 manage.py runserver

