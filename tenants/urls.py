from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [

    path('create/maintenant', views.create_tenant, {'is_maintenant': True}, name='MainTenantCreate'),
    path('create/subtenant', views.create_tenant, {'is_maintenant': False}, name='SubTenantCreate'),
    path('view/<int:pk>', views.view_tenant, name='TenantView'),
    path('update/<int:pk>', views.update_tenant, name='TenantUpdate'),
    path('delete/<int:pk>', views.delete_tenant, name='TenantDelete'),

]
