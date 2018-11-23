"use strict";

document.getElementById('view_maintenant').href = '/tenants/view/' + document.getElementById('id_maintenant').value;
document.getElementById('view_subtenant').href = '/tenants/view/' + document.getElementById('id_subtenant').value;

document.getElementById('id_maintenant').onchange = function set_maintenant() {
    let id = document.getElementById('id_maintenant').value;
    document.getElementById('view_maintenant').href = '/tenants/view/' + id
};

document.getElementById('id_subtenant').onchange = function set_maintenant() {
    let id = document.getElementById('id_subtenant').value;
    document.getElementById('view_subtenant').href = '/tenants/view/' + id
};