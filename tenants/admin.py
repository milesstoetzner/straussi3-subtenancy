from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import User, MainTenant, SubTenant, Blacklist


admin.site.register(User, SimpleHistoryAdmin)
admin.site.register(MainTenant, SimpleHistoryAdmin)
admin.site.register(SubTenant, SimpleHistoryAdmin)
admin.site.register(Blacklist, SimpleHistoryAdmin)
