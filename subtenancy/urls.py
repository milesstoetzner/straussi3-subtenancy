from django.contrib import admin
from django.urls import include, path
from tenants import views as tenant_views
from . import views

urlpatterns = [

    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),
    path('profile/', tenant_views.view_profile, name='Profile'),
    # path('profile/delete', tenant_views.delete_profile, name='ProfileDelete'),
    path('profile/update', tenant_views.update_profile, name='ProfileUpdate'),
    path('profile/updateRequest', tenant_views.update_request, name='RequestUpdate'),
    path('requests/', tenant_views.query_requests, name='Requests'),
    path('impressum/', views.legal_notice, name='Impressum'),
    path('tenants/', include('tenants.urls')),
    path('contracts/', include('contracts.urls')),

    path('register/maintenant', tenant_views.create_tenant, {'is_maintenant': True}, name='MainTenantCreate'),
    path('register/subtenant', tenant_views.create_tenant, {'is_maintenant': False}, name='SubTenantCreate'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('password_change/', views.PasswordChange.as_view(), name='password_change'),

    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/callback/<uidb64>/<token>/', views.PasswordResetCallback.as_view(), name='password_reset_confirm'),

    path('i18n/', include('django.conf.urls.i18n')),

]


handler400 = views.handler400
handler403 = views.handler403
handler404 = views.handler404
handler500 = views.handler500
