from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [

    # in regards to UX the create routes are listed in subtenancy/urls.py
    # path('create/maintenant', views.create_tenant, {'is_maintenant': True}, name='MainTenantCreate'),
    # path('create/subtenant', views.create_tenant, {'is_maintenant': False}, name='SubTenantCreate'),
    path('view/<int:pk>', views.view_tenant, name='TenantView'),
    path('update/<int:pk>', views.update_tenant, name='TenantUpdate'),
    # delete route is listed in subtenancy/urls.py
    path('contact/<int:pk>', views.contact_subtenant, name='SubTenantContact'),
    path('blacklist/', views.blacklist, name='Blacklist'),

]
