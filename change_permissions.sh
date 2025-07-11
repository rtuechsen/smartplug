
# This script changes the permissions of files and directories relevant to the smartplug-dirigent
# such that the default user of the ubuntu system cannot modify or delete them without providing
# a password. The permissions have to be low enough to allow the system to work.

# nginx

sudo chown -R root:root /etc/nginx/
sudo chmod -R 645 /etc/nginx/							# other users = 5 needed to allow the 'cd' command to work

sudo chown -R root:root /etc/nginx/ssl/
sudo chmod -R 640 /etc/nginx/ssl/						# other users = 0 so that they cannot read the secret

# service

sudo chown root:root /etc/systemd/system/
sudo chmod 755 /etc/systemd/system/

# mosquitto

sudo chown -R root:root /etc/mosquitto
sudo chmod -R 645 /etc/mosquitto

sudo chown root:www-data /etc/mosquitto/mosquitto_passwd.json
sudo chmod 660 /etc/mosquitto/mosquitto_passwd.json		# other users = 0 so that they cannot read the secret

sudo chown root:mosquitto /etc/mosquitto/passwd
sudo chmod 660 /etc/mosquitto/passwd					# other users = 0 so that they cannot read the secret

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
