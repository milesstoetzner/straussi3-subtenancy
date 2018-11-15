# Ferienmiete

## Routes

| Route | Description | Permission |
| --- | --- | --- |
| /login | | | 
| /logout | | | 
| | | |
| /tenants/create/\<string:type> | |  |
| /tenants/view/\<int:pk> | | is_staff or is_owner |
| /tenants/update/\<int:pk> | | is_staff or is_owner |
| /tenants/delete/\<int:pk> | | is_staff or is_owner |
| /tenants/contact/\<int:pk> | | is_maintenant or is_subtenant |
| | | |
| /contracts/create | | is_staff |
| /contracts/view/\<int:pk> | | is_staff |
| /contracts/pdf/\<int:pk> | | is_staff |
| /contracts/update/\<int:pk> | | is_staff |
| | | |
| /active | | is_staff or is_external |
| /archive | | is_staff or is_external|
| | | |
| / |  |  |
| /search |  | is_staff |
| /impressum | | |