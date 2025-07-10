
# TODO: add explanation

# nginx

sudo chown -R root:root /etc/nginx/
sudo chmod -R 644 /etc/nginx/

sudo chown -R root:root /etc/nginx/ssl/
sudo chmod -R 640 /etc/nginx/ssl/



# service

sudo chown root:root /etc/systemd/system/
sudo chmod 755 /etc/systemd/system/


# mosquitto

sudo chown -R root:root /etc/mosquitto
sudo chmod -R 645 /etc/mosquitto


# logs

sudo chown -R root:root /var/log/nginx/
sudo chmod -R 655 /var/log/nginx/

sudo chown -R mosquitto:mosquitto /var/log/mosquitto/
sudo chmod -R 755 /var/log/mosquitto/

sudo chown -R www-data:www-data /var/log/smartplug_app/
sudo chmod -R 755 /var/log/smartplug_app/



# static web files

sudo chown -R root:root /var/www/html/
sudo chmod -R 755 /var/www/html/

sudo chown root:root /etc/logrotate.d/
sudo chmod 755 /etc/logrotate.d/

sudo chown -R root:www-data /opt/smartplug-dirigent/
sudo chmod -R 775 /opt/smartplug-dirigent/
