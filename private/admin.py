from django.contrib import admin
from .models import Contract, Administrative
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class AdministrativeInline(admin.StackedInline):
    model = Administrative
    can_delete = False
    verbose_name_plural = 'Wohnheimscope'


class UserAdmin(BaseUserAdmin):
    inlines = (AdministrativeInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Contract)
