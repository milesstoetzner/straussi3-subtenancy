from django.contrib import admin
from django.urls import include, path
from tenants import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # TODO: only login
    path('offers/', views.Offers.as_view(), name='Offers'),
    path('requests/', views.Requests.as_view(), name='Requests'),
    path('impressum/', views.legal_notice, name='Impressum'),
    path('tenants/', include('tenants.urls')),
    path('contracts/', include('contracts.urls'))

    # TODO: report bug
]