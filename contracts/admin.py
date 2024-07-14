from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Contract, Roster


admin.site.register(Contract, SimpleHistoryAdmin)
admin.site.register(Roster, SimpleHistoryAdmin)
