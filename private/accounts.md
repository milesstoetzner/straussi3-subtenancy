# Permissions and Authorization

## Groups

- Assistants
- External
- Staff
- Superuser

### Assistants

- Each residential home owns one (or more) account(s) of this group
- Users of this group are scoped to their residential home
- Permissions: 
    - view contracts
    - add contracts
    - update contracts
    - view maintenants
    - add maintenants
    - update maintenants
    - delete maintenants
    - view subtenants
    - add subtenants
    - update subtenants
    - delete subtenants
    
### External

- Each residential home janitor and contact person at the SWS owns one account of this group
- Users of this group are scoped to their residential home
- Permissions:
    - view running contracts

### Staff
undefined

### Superuser
Corresponds to django's superuser.