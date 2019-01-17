from django.contrib import admin
from django.urls import include, path
from tenants import views as tenant_views
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),
    path('profile/', tenant_views.view_profile, name='Profile'),
    path('profile/delete', tenant_views.delete_profile, name='ProfileDelete'),
    path('profile/update', tenant_views.update_profile, name='ProfileUpdate'),
    path('requests/', tenant_views.Requests.as_view(), name='Requests'),
    path('impressum/', views.legal_notice, name='Impressum'),
    path('tenants/', include('tenants.urls')),
    path('contracts/', include('contracts.urls')),

    path('register/maintenant', tenant_views.create_tenant, {'is_maintenant': True}, name='MainTenantCreate'),
    path('register/subtenant', tenant_views.create_tenant, {'is_maintenant': False}, name='SubTenantCreate'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/change/', views.PasswordChange.as_view(), name='password_change'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
