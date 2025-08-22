# Straussi3 Subtenancy

Django app for administrating the subtenancy for the Straussi3.

- Link: https://untermiete.straussi3.de
- Link (alternative): https://str3-new.ext.selfnet.de
- Repo: https://github.com/milesstoetzner/straussi3-subtenancy
- Website: https://straussi3.de

## Development

### Permissions

To set up the permission groups see [permissions](/config/permissions).

### Database

The database is not seeded.
You may import a production database backup.
Therefore, download the backup, extract it, and adjust the following:

1. migrate `djangouser` to `"default"`
2. migrate `postgres` to `"default"`
3. migrate `COPY` to `\copy`
4. remove any `$$PATH$$`

Then import the backup as follows

```
psql -h localhost -U default -d subtenancy -f restore.sql
```

To create a superuser use a SQL command.
`python manage.py createsuperuser` will not work since the user model is not the original one.
The database scheme can be found [here](/config/database.pdf).

## Deployment

### Server

The production system is deployed on a server hosted on Selfnet.
See [Vagrantfile](Vagrantfile) for deployment.
Note that the Vagrantfile is more conceptual and not a fully working example.

### SSH

You may add the following entry to your `.ssh/config`.

```
Host untermiete
    hostname untermiete.straussi3.de
    identityfile ~/.ssh/id_rsa
    user str3
```

### Release

New releases are deployed manually on the server using `untermiete:~/pull.sh`.

### Backups

A [cronjob](/config/cronjob) backs up the database every night using `untermiete:~/backup.sh`.
Therefore, the database `subtenancy` is dumped and together with all contract pdf files.
To dump the database you need to set up the password in [.pgpass](/config/.pgpass).

### Emails

The production system sends email notifications using the following account.
This email is send-only.
All incoming emails are forwarded to wore.str3@gmail.com for further processing.

- Email: untermiete@straussi3.de
- Inbox: https://mail.ext.selfnet.de/SOGo
- Account: https://mail.ext.selfnet.de/

### Clean Database

```
python manage.py clean_database
```

### Environment

| Environment Variable                    | Default Value        | Description                                                      |
|-----------------------------------------|----------------------|------------------------------------------------------------------|
| `SUBTENANCY_SECRET_KEY`                 |                      | Django secret key (must be set for production).                  |
| `SUBTENANCY_DEBUG`                      | `'0'`                | Enables debug mode if set to `'1'`.                              |
| `SUBTENANCY_ALLOWED_HOSTS`              | `'localhost'`        | Comma-separated list of allowed hosts.                           |
| `SUBTENANCY_ORIGIN`                     | `'http://localhost'` | Used for setting request origin (e.g. for CORS).                 |
| `SUBTENANCY_EMAIL_HOST`                 |                      | Email server hostname or IP address.                             |
| `SUBTENANCY_EMAIL_PORT`                 | `587`                | Email server port.                                               |
| `SUBTENANCY_EMAIL_HOST_USER`            |                      | Email login username.                                            |
| `SUBTENANCY_EMAIL_HOST_PASSWORD`        |                      | Email login password.                                            |
| `SUBTENANCY_EMAIL_USE_TLS`              | `'1'`                | Enable TLS for email connection.                                 |
| `SUBTENANCY_EMAIL_DEFAULT_FROM`         |                      | Default sender email address.                                    |
| `SUBTENANCY_EMAIL_SERVER`               |                      | Server email address used by Django error emails.                |
| `SUBTENANCY_DB_NAME`                    | `'subtenancy'`       | PostgreSQL database name.                                        |
| `SUBTENANCY_DB_USER`                    | `'default'`          | Database username.                                               |
| `SUBTENANCY_DB_PASSWORD`                | `'default'`          | Database password.                                               |
| `SUBTENANCY_DB_HOST`                    | `'127.0.0.1'`        | Database host.                                                   |
| `SUBTENANCY_DB_PORT`                    | `'5432'`             | Database port.                                                   |
| `SUBTENANCY_SECURE_PROXY_SSL_HEADER`    |                      | Header and value tuple for SSL offloading (parsed into a tuple). |
| `SUBTENANCY_SESSION_COOKIE_SECURE`      | `'1'`                | Require HTTPS for session cookie.                                |
| `SUBTENANCY_SESSION_CSRF_COOKIE_SECURE` | `'1'`                | Require HTTPS for CSRF cookie.                                   |
| `SUBTENANCY_CLEAN_DATABASE_WRITE`       | `'0'`                | Custom feature toggle for clean DB write logic.                  |
| `SUBTENANCY_ENABLE_MIGRATIONS`          | `'0'`                | Run database migrations.                                         |
| `SUBTENANCY_USE_X_FORWARDED_HOST`       | `'0'`                |                                                                  |
