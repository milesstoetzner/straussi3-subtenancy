# Ferienmiete

Eine Web Anwendung für die Verwaltung der Ferienmiete des Studentenwohnheims Straußäcker 3.

## Documentation

### Maintenant/Subtenant

#### Create Maintenant/Subtenant

To create a new maintenant or subtenant visit the route `/register/maintenant` resp. `/register/subtenant`.
Each tenant has to create a new account and provide additional conditional personal information.
After registration every tenant receives a unique `id`.
The requested/stored information can be found in [Database Overview](/doc/database.pdf).

#### Update Maintenant/Subtenant

To update an existing maintenant or subtenant you have to visit `/tenant/update/<id>` where `<id>` is the tenant's `id`. 
The assistant and the tenant are allowed to update the tenant's account (therefore the tenant has to visit `/profile/update`).

#### Delete Maintenant/Subtenant

Only the tenant himself can delete his account and only if there are no contracts.
Therefore he has to visit `/profile/delete`.

#### Change or Reset Password

Only the tenant himself can change or reset his account password.
* To change his password visit `/password_change` (the tenant needs to be logged in).
* To reset his password visit `password_reset` (the tenant needs access to his email account).


#### Contact Subtenant

Only a maintenant can contact a subtenant.
Therefore he can visit `/requests`, select the desired request and send an email containing his contact details to the corresponding subtenant.
To protect the subtenants privacy the email is sent using our email account - therefore the maintenant does not get any knowledge about the subtenant.

#### Blacklist

There exists are two lists containing blocked `student_id`s and `tenant_id`s (see `/tenants/blacklist`). 
Contracts related to a blocked tenant can not be created/changed.
To create/change/delete an entry of those lists contact the admin.


#### Inactive

Inactive tenants are not allowed to login
. Therefore the admin has to set the corresponding tenant to `inactive`.

#### History

Each change to the tenant is stored permanently - including login times.

### Search for Maintenant/Subtenant or Contract


### Contract

#### Create Contract
#### Update Contract
#### Delete Contract
#### Inactive Contract

#### Running Contracts

All current active contracts are listed in `/contracts/active`.

#### Archive

All inactive contracts are listed in `/contracts/archive`.


#### History

Each change to the contract is stored permanently.

#### SWS

The SWS expects each month a list of all active contracts. The list can be accessed at `/contracts/print`. 



### Apps
- `contracts`: Verwaltung der Verträge
- `subtenancy`: Projekt allgemein - Authentifizierung, öffentliche Inhalte, geteilte Ressourcen (diese sind allerdings im Ordner `tenants` gespeichert ...)
- `tenants`: Verwaltung der Haupt-/Untermieter

### Groups and Permissions
- `Maintenant`:
    - `tenants.change_own`
    - `tenants.delete_own`
    - `tenants.contact_subtenant`
- `Subtenant`
    - `tenants.change_own`
    - `tenants.delete_own`
- `Assistant`
    - `tenants.view_user`
    - `tenants.change_user`
    - `tenants.view_maintenant`
    - `tenants.change_maintenant`
    - `tenants.view_subtenant`
    - `tenants.change_subtenant`
    - `tenants.view_blockedtenantid`
    - `tenants.view_blockedstudentid`
    - `contract.add_contract`
    - `contract.view_contract`
    - `contract.view_short_contract`
    - `contract.change_contract`
- `External`
    - `tenants.view_short_contract`