
# TODO: add explanation

# nginx

# sudo chown root:root /etc/nginx/nginx.conf
# sudo chmod 640 /etc/nginx/nginx.conf

sudo chown -R root:root /etc/nginx/nginx.conf
sudo chmod -R 644 /etc/nginx/nginx.conf

sudo chown root:root /etc/nginx/ssl/
sudo chmod 640 /etc/nginx/ssl/



# service

sudo chown root:root /etc/systemd/system/gunicorn.service
sudo chmod 644 /etc/systemd/system/gunicorn.service


# mosquitto

# sudo chown root:root /etc/mosquitto/mosquitto.conf
# sudo chmod 640 /etc/mosquitto/mosquitto.conf

# sudo chown -R mosquitto: /etc/mosquitto/passwd
# sudo chmod -R 600 /etc/mosquitto/passwd

sudo chown -R root:root /etc/mosquitto
sudo chmod -R 644 /etc/mosquitto

sudo chown mosquitto: /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd


# logs

sudo chown root:root /var/log/nginx/
sudo chmod 644 /var/log/nginx/

sudo chown root:root /var/log/mosquitto/
sudo chmod 644 /var/log/mosquitto/

sudo chown root:root /var/log/smartplug_app
sudo chmod 644 /var/log/smartplug_app



# static web files

sudo chown root:root /var/www/html/
sudo chmod 754 /var/www/html/

sudo chown root:root /etc/logrotate.d/smartplug_app
sudo chmod 644 /etc/logrotate.d/smartplug_app

sudo chown root:root /opt/smartplug-dirigent
sudo chmod 754 /opt/smartplug-dirigent



