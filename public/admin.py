from django.contrib import admin
from .models import User, MainTenant, SubTenant, ResidentialHome


admin.site.register(User)
admin.site.register(MainTenant)
admin.site.register(SubTenant)
admin.site.register(ResidentialHome)
