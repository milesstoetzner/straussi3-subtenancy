from django.contrib import admin
from django.urls import include, path
from tenants import views as tenant_views
from . import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),
    path('profile/', tenant_views.view_profile, name='Profile'),
    path('requests/', tenant_views.Requests.as_view(), name='Requests'),
    path('impressum/', views.legal_notice, name='Impressum'),
    path('tenants/', include('tenants.urls')),
    path('contracts/', include('contracts.urls')),

    path('register/maintenant', tenant_views.create_tenant, {'is_maintenant': True}, name='MainTenantCreate'),
    path('register/subtenant', tenant_views.create_tenant, {'is_maintenant': False}, name='SubTenantCreate'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/change/', views.PasswordChange.as_view(), name='password_change'),
    path('password/reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password/reset/<slug:uidb64>/<slug:token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
]
