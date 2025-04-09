
export DJANGO_PIPELINE=development

sudo systemctl stop nginx

python3 manage.py makemigrations

python3 manage.py migrate

python3 manage.py runserver

# npm run build
# npm start
# debug using: `npm run dev`  

