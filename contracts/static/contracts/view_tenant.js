"use strict";

// Puts a square "open tenant" button next to the maintenant and subtenant selects of the contract form.
// The button links to the tenant currently chosen in the select (opens in a new tab).
["maintenant", "subtenant"].forEach(function (name) {
    const select = document.getElementById("id_" + name);
    if (!select) {
        return;
    }

    const link = document.createElement("a");
    link.id = "view_" + name;
    link.className = "btn btn-primary btn-icon";
    link.target = "_blank";
    link.title = (name === "maintenant" ? "Hauptmieter" : "Untermieter") + " anzeigen";
    link.innerHTML = '<i class="fas fa-user"></i>';

    const row = document.createElement("div");
    row.className = "with-addon";
    select.parentNode.insertBefore(row, select);
    row.appendChild(select);
    row.appendChild(link);

    function update() {
        link.href = "/tenants/view/" + select.value;
        link.classList.toggle("disabled", !select.value);
    }
    select.addEventListener("change", update);
    update();
});
