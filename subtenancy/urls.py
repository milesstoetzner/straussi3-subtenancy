from django.contrib import admin
from django.urls import include, path
from tenants import views as tenant_views
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', tenant_views.index, name='Index'),
    path('admin/', admin.site.urls),
    path('offers/', tenant_views.Offers.as_view(), name='Offers'),
    path('requests/', tenant_views.Requests.as_view(), name='Requests'),
    path('impressum/', tenant_views.legal_notice, name='Impressum'),
    path('tenants/', include('tenants.urls')),
    path('contracts/', include('contracts.urls')),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),

    # TODO: path('report/', views.ReportBug.as_view(), name='report_bug')
]
