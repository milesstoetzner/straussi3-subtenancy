from django.contrib import admin
from .models import MainTenant, SubTenant


admin.site.register(MainTenant)
admin.site.register(SubTenant)
