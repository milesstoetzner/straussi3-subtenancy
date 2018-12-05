# Ferienmiete

Eine Web Anwendung für die Verwaltung der Ferienmiete des Studentenwohnheims Straußäcker 3.

## Overview

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


## Instructions

### Deployment

### Maintenant/Subtenant

#### Create Maintenant/Subtenant
#### Update Maintenant/Subtenant
#### Delete Maintenant/Subtenant
#### Contact Subtenant
#### Blacklist

### Search for Maintenant/Subtenant or Contract

### Contract

#### Create Contract
#### Update Contract
#### Delete Contract
#### Running Contracts
#### Archive