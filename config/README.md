# ferienmiete.conf - nginx server block (vhost)
/etc/nginx/sites/available/ferienmiete.conf

# uwsgi.service - uWSGI systemd service file
/etc/systemd/system/uwsgi.service

# ferienmiete.ini - uWSGI Python/Django App ini file
/etc/uwsgi/sites/ferienmiete.ini

# Replace self signed certificates using certbot!

# Create superuser
INSERT INTO tenants_user VALUES (1, 'pbkdf2_sha256$120000$68wqVJEAgJ84$/1HENU9SyRkn4QDdaLuzOGOOjHT77jP1RNuNRyhOLjc=', '2019-02-18 19:05:26.631898', true, 'admin', true, true, '2018-11-22 21:04:04', 'Miles', 'Stötzner', 'miles.stoetzner@googlemail.com', '1995-07-21', 01777580061, false, false, false, false, '2018-11-22 21:04:04.075903', '2018-11-22 21:04:04.075903');
Password: PYicLChYtCZ59Cf