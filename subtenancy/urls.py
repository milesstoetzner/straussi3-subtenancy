from django.contrib import admin
from django.urls import include, path
from tenants import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),  # TODO: only login
    path('accounts/', include('django.contrib.auth.urls')),
    path('hauptmieter/', views.MainTenantCreate.as_view(), name='MainTenantCreate'),
    path('untermieter/', views.SubTenantCreate.as_view(), name='SubTenantCreate'),
    path('angebote/', views.Offers.as_view(), name='Offers'),
    path('anfragen/', views.Requests.as_view(), name='Requests'),
    path('impressum/', views.legal_notice, name='Impressum'),
    path('contracts/', include('contracts.urls'))
]