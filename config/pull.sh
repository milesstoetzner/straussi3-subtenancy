#!/bin/sh


# git pull
cd /var/www/ferienmiete
sudo -u www-data git pull

#sudo -u www-data python3 manage.py makemigrations
sudo -u www-data python3 manage.py migrate

#sudo -u www-data python3 manage.py collectstatic

sudo -u www-data python3 manage.py compilemessages
cd ~

# restart uwsgi
sudo systemctl restart uwsgi.service

echo Restarted uswsgi
echo Done