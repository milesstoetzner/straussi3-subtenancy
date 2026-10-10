from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm
from django.forms import modelform_factory
from django.utils.translation import gettext_lazy as _
from .models import User, MainTenant, SubTenant, SubtenancyRequest, Blacklist


class TenantUserAdmin(UserAdmin):
    """
    Django's UserAdmin (read-only password hash, "set password" form, working "add user" form), extended with
    whatever fields our user models add on top of the stock user. The extra fields are read from the model,
    so new model fields show up here without touching this file.
    """

    list_display = ('username', 'first_name', 'last_name', 'email', 'type', 'is_active')
    list_filter = ('type',) + UserAdmin.list_filter

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # the add form must create *this* model (MainTenant/SubTenant), not the base User
        self.add_form = modelform_factory(model, form=AdminUserCreationForm)

    def _extra_fields(self):
        known = {name for _, opts in UserAdmin.fieldsets for name in opts['fields']}
        return [
            f.name for f in self.model._meta.fields
            if f.editable and f.name not in known and f.name != 'id'
            and not (f.remote_field and f.remote_field.parent_link)
        ]

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return ((None, {'fields': ('username', 'usable_password', 'password1', 'password2', *self._extra_fields())}),)
        return (*UserAdmin.fieldsets, (_('Mieter'), {'fields': self._extra_fields()}))


class SubtenancyRequestInline(admin.StackedInline):
    model = SubtenancyRequest
    extra = 0


class SubTenantAdmin(TenantUserAdmin):
    inlines = (SubtenancyRequestInline,)


@admin.register(SubtenancyRequest)
class SubtenancyRequestAdmin(admin.ModelAdmin):
    list_display = ('subtenant', 'begin', 'end', 'updated_at')
    search_fields = ('subtenant__username', 'subtenant__first_name', 'subtenant__last_name', 'subtenant__email')
    autocomplete_fields = ('subtenant',)


admin.site.register(User, TenantUserAdmin)
admin.site.register(MainTenant, TenantUserAdmin)
admin.site.register(SubTenant, SubTenantAdmin)
admin.site.register(Blacklist)
