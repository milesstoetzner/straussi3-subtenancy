# Permissions and Authorization

### is_assistant

- Each residential home owns one (or more) account(s) with this flag
- Users with this flag are scoped to their residential home
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
    
### is_external

- Each residential home janitor and contact person at the SWS owns one account with this flag
- Users with this flag are scoped to their residential home
- Permissions:
    - view running contracts

### Staff
undefined

### Superuser
Corresponds to django's superuser.