from django.contrib import admin
from .models import User, MainTenant, SubTenant, Blacklist


admin.site.register(User)
admin.site.register(MainTenant)
admin.site.register(SubTenant)
admin.site.register(Blacklist)
