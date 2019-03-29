# Ferienmiete

Django app for administrating the subtenancy of the residential home [Straußäcker 3](https://www.studierendenwerk-stuttgart.de/wohnen/wohnanlagen/straussaecker-iii/).
A live demo can be seen [here](https://str3.ext.selfnet.de/).

## Deployment

See [Vagrantfile](/config/Vagrantfile) for deployment. Note that the Vagrantfile is more conceptual and not a fully working example.

To create a superuser use a SQL command. `python manage.py createsuperuser` will not work since the user model is not the original one.
The database scheme can be found [here](/config/database.pdf).

A [cronjob](/config/cronjob) backs up the database every night. Therefore the database `subtenancy` is dumped and together with all contract pdf files encrypted and uploaded to [Google Drive](https://www.google.com/drive/). 
Therefore install [gdrive](https://github.com/gdrive-org/gdrive) using this [tutorial](https://github.com/gdrive-org/gdrive/issues/426).
To dump the database you need to set up the password in [.pgpass](/config/.pgpass).

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
    - `tenants.view_fameofhall`
    - `contract.add_contract`
    - `contract.view_contract`
    - `contract.view_short_contract`
    - `contract.change_contract`
- `External`
    - `tenants.view_short_contract`