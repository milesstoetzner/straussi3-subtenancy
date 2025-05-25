# Straussi3 Subtenancy

Django app for administrating the subtenancy for the Straussi3.

## Production System

- https://untermiete.straussi3.de
- https://str3.ext.selfnet.de


## Repository 

- https://github.com/milesstoetzner/straussi3-subtenancy


## Development 

1. Copy `.SECRETS.py` to `subtenancy/SECRETS.py`. Never commit this file! It is ignored by git by default.
2. Start the docker compose file, e.g., `docker compose up -d`
3. Visit http://localhost:8000
4. Stop the local system, e.g., `docker compose down`. To also purge the database, run `docker compose down -v`.

## Database 

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


## Deployment

See [Vagrantfile](Vagrantfile) for deployment. Note that the Vagrantfile is more conceptual and not a fully working example.

To create a superuser use a SQL command. `python manage.py createsuperuser` will not work since the user model is not the original one.
The database scheme can be found [here](/config/database.pdf).

A [cronjob](/config/cronjob) backs up the database every night.
Therefore, the database `subtenancy` is dumped and together with all contract pdf files.
To dump the database you need to set up the password in [.pgpass](/config/.pgpass).

To set up the permission groups see [permissions](/config/permissions).
