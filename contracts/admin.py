from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Contract


admin.site.register(Contract, SimpleHistoryAdmin)
