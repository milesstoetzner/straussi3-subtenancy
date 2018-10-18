from django.contrib import admin
from .models import MainTenant, SubTenant, ResidentialHome


admin.site.register(MainTenant)
admin.site.register(SubTenant)
admin.site.register(ResidentialHome)
