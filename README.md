# Ferienmiete

Eine Web Anwendung für die Verwaltung der Ferienmiete des Studentenwohnheims Straußäcker 3.

## Documentation

### Tutorial

Information on how to use this website can be found under `/` and `contracts/help`.

### Database Scheme

The database scheme can be found here: [Database Schema](/doc/database.pdf).

### Apps
- `contracts`: Verwaltung der Verträge
- `subtenancy`: Projekt allgemein - Authentifizierung, öffentliche Inhalte, geteilte Ressourcen (diese sind allerdings im Ordner `tenants` gespeichert ...)
- `tenants`: Verwaltung der Haupt-/Untermieter

## Deployment

### nginx configuration
```
# /etc/nginx/sites/available/ferienmiete.conf

# the upstream component nginx needs to connect to
upstream django {
  #server unix:///tmp/subtenancy.sock;
  server unix:///var/run/uwsgi/subtenancy.sock;
    # server 127.0.0.1:8001; # for a web port socket (we'll use this first)
}

server {
        server_name 127.0.0.1 [::1] localhost ferienmiete.straussi3.de str3.ext.selfnet.de;

        location /static {
                alias /var/www/ferienmiete/static;
        }

        location / {
                uwsgi_pass django;
                include /var/www/ferienmiete/config/uwsgi_params;
        }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/str3.ext.selfnet.de/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/str3.ext.selfnet.de/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    listen      443 ssl default_server;
    server_name 127.0.0.1 0.0.0.1 localhost ferienmiete.straussi3.de str3.ext.selfnet.de;

    ssl_certificate     /etc/letsencrypt/live/str3.ext.selfnet.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/str3.ext.selfnet.de/privkey.pem;
    ssl_ciphers         EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH;
    ssl_protocols       TLSv1.1 TLSv1.2;

    location /static {
        alias /var/www/ferienmiete/static; # your Django project's static files - amend as required
    }

    location / {
        uwsgi_pass  django;
        include     /var/www/ferienmiete/config/uwsgi_params;
    }
}



server {
    if ($host = str3.ext.selfnet.de) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


        listen  80 default_server;
        server_name 127.0.0.1 [::1] localhost ferienmiete.straussi3.de str3.ext.selfnet.de;
    return 404; # managed by Certbot


}
```

### uwsgi.service - uWSGI systemd service file
```
# /etc/systemd/system/uwsgi.service
[Unit]
Description=uWSGI Emperor service

[Service]
#ExecStartPre=/bin/bash -c 'mkdir -p /var/run/uwsgi; chown www-data:www-data /var/run/uwsgi'
ExecStart=/usr/bin/uwsgi_python3 --emperor /etc/uwsgi/sites --uid www-data --gid www-data --venv /var/www/ferienmiete/
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

### ferienmiete.ini - uWSGI Python/Django App ini file
```
# /etc/uwsgi/sites/ferienmiete.ini
[Unit]
Description=uWSGI Emperor service

[Service]
#ExecStartPre=/bin/bash -c 'mkdir -p /var/run/uwsgi; chown www-data:www-data /var/run/uwsgi'
ExecStart=/usr/bin/uwsgi_python3 --emperor /etc/uwsgi/sites --uid www-data --gid www-data --venv /var/www/ferienmiete/
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target

str3@str3:~$ cat /etc/uwsgi/sites/ferienmiete.ini
# subtenancy_uwsgi.ini file
[uwsgi]

# Django-related settings
# the base directory (full path)
chdir           = /var/www/ferienmiete/
# Django's wsgi file
module          = subtenancy.wsgi
# the virtualenv (full path)
home            = /var/www/ferienmiete/

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /var/run/uwsgi/subtenancy.sock
# ... with appropriate permissions - may be needed
chmod-socket    = 666
# clear environment on exit
vacuum          = true
# logs
daemonize = /var/www/log
```

### Certificate
To generate a valid certificate use [certbot](https://certbot.eff.org/) in combination with nginx.

### Database
Install a [PostgreSQL](https://www.postgresql.org/) database and create a user `djangouser`.

### Create superuser/admin
To create a superuser the command `python manage.py createsuperuser` will not work since user model is not the original one.
Therefore, execute the following SQL command:
```
INSERT INTO tenants_user VALUES (1, 'pbkdf2_sha256$120000$68wqVJEAgJ84$/1HENU9SyRkn4QDdaLuzOGOOjHT77jP1RNuNRyhOLjc=', '2019-02-18 19:05:26.631898', true, 'admin', true, true, '2018-11-22 21:04:04', 'Miles', 'Stötzner', 'miles.stoetzner@googlemail.com', '1995-07-21', 01777580061, false, false, false, false, '2018-11-22 21:04:04.075903', '2018-11-22 21:04:04.075903');
Password: PYicLChYtCZ59Cf
```

### Groups and Permissions
The following groups need to exist with the corresponding permissions:

- `Maintenant`:
    - `tenants.change_own`
    - `tenants.contact_subtenant`
- `Subtenant`
    - `tenants.change_own`
- `Assistant`
    - `tenants.view_user`
    - `tenants.change_user`
    - `tenants.view_maintenant`
    - `tenants.change_maintenant`
    - `tenants.view_subtenant`
    - `tenants.change_subtenant`
    - `tenants.view_blacklist`
    - `contract.add_contract`
    - `contract.view_contract`
    - `contract.view_short_contract`
    - `contract.change_contract`
- `External`
    - `tenants.view_short_contract`

### Backup

A cronjob backs up the database every night. Therefore the database `subtenancy` is dumped and together with all contract pdf files uploaded to [Google Drive](https://www.google.com/drive/). 
Therefore install [gdrive](https://github.com/gdrive-org/gdrive).

```
# Cronjob
# Backup subtenancy data every day at 02:20
20 2 * * * /home/str3/backup.sh
```

```
# .pgpass
localhost:5432:subtenancy:djangouser:***********
```

```
# backups.sh
#!/bin/bash

# A simple script to backup subtenancy data and upload them to Google Drive

GDRIVE=1xXQ_LfwxPMNvJvJowW1EB-KeTudeWOG5
BACKUP=/home/str3/backups/
CONTRACTS=/var/www/ferienmiete/contracts/contracts/
DBUSER=djangouser
DBNAME=subtenancy
DBHOST=localhost
DATE=$(date +"%Y-%m-%d")

# Create tar containing dump of database and all contract pdf files

mkdir -p $BACKUP
tar -cf ${BACKUP}contracts.tar -C $CONTRACTS .
pg_dump -h $DBHOST -U $DBUSER -w -F t $DBNAME -f ${BACKUP}subtenancy.tar
tar -cf ${BACKUP}subtenancy_backup_${DATE}.tar ${BACKUP}contracts.tar ${BACKUP}subtenancy.tar -C $BACKUP

# Upload backup to gdrive
/usr/local/bin/gdrive upload --parent $GDRIVE ${BACKUP}subtenancy_backup_${DATE}.tar

# Cleanup files
# find /backups/postgres_backups -name "customerdata*.gz" -mtime +30 -type f -delete
rm ${BACKUP}contracts.tar
rm ${BACKUP}subtenancy.tar
```

### Additional configurations

There are more necessary server configurations like `nftables`, `apticron`, `Unattended-Upgrade`.
Consult [selfnet](https://www.selfnet.de/) for help.  
