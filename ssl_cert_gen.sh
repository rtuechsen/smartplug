
sudo mkdir /etc/nginx/ssl/

# TODO: fill in options automatically

sudo openssl genpkey -algorithm RSA -out /etc/nginx/ssl/selfsigned.key

sudo openssl req -new -x509 -key /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -days 365
