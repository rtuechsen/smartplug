
# TODO: add explanation

# nginx

# sudo chown root:root /etc/nginx/nginx.conf
# sudo chmod 640 /etc/nginx/nginx.conf

sudo chown -R root:root /etc/nginx/
sudo chmod -R 644 /etc/nginx/

sudo chown -R root:root /etc/nginx/ssl/
sudo chmod -R 640 /etc/nginx/ssl/



# service

sudo chown root:root /etc/systemd/system/
sudo chmod 755 /etc/systemd/system/


# mosquitto

# sudo chown root:root /etc/mosquitto/mosquitto.conf
# sudo chmod 640 /etc/mosquitto/mosquitto.conf

# sudo chown -R mosquitto: /etc/mosquitto/passwd
# sudo chmod -R 600 /etc/mosquitto/passwd

sudo chown -R root:root /etc/mosquitto
sudo chmod -R 645 /etc/mosquitto

sudo chown mosquitto: /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd


# logs

sudo chown -R root:root /var/log/nginx/
sudo chmod -R 645 /var/log/nginx/

sudo chown -R root:root /var/log/mosquitto/
sudo chmod -R 645 /var/log/mosquitto/

sudo chown -R root:root /var/log/smartplug_app/
sudo chmod -R 645 /var/log/smartplug_app/



# static web files

sudo chown -R root:root /var/www/html/
sudo chmod -R 755 /var/www/html/

sudo chown root:root /etc/logrotate.d/
sudo chmod 755 /etc/logrotate.d/

sudo chown -R root:www-data /opt/smartplug-dirigent/
sudo chmod -R 775 /opt/smartplug-dirigent/



