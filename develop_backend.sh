
export DJANGO_PIPELINE=development

cd backend

sudo systemctl stop nginx

python3 manage.py makemigrations

python3 manage.py migrate

uvicorn shelly_dirigent.asgi:application


