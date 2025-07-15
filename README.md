# Straussi3 Subtenancy

Django app for administrating the subtenancy for the Straussi3.

- Link: https://untermiete.straussi3.de
- Link (alternative): https://str3.ext.selfnet.de
- Repo: https://github.com/milesstoetzner/straussi3-subtenancy
- Website: https://straussi3.de

## Development

### Docker

1. Copy `.SECRETS.py` to `subtenancy/SECRETS.py`. Never commit this file! It is ignored by git by default.
2. Start the docker compose file, e.g., `docker compose up` or `docker compose up -d`.
3. Visit ... 
   - http://localhost:8000
   - http://localhost:8000/admin
   - http://localhost:8080/?pgsql=database&username=default&db=subtenancy
4. Stop the local system, e.g., `docker compose down`. To also purge the database, run `docker compose down -v`.

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
All incoming emails are forwarded to wore.str3@gmail.com for futher processing.

- Email: untermiete@straussi3.de
- Inbox: https://mail.ext.selfnet.de/SOGo
- Account: https://mail.ext.selfnet.de/

