from django.contrib import admin
from django.urls import include, path
from public import views

urlpatterns = [
    path('', views.index, name='Index'),
    path('admin/', admin.site.urls),  # TODO: only login
    path('accounts/', include('django.contrib.auth.urls')),
    path('hauptmieter/', views.MainTenantCreate.as_view(), name='MainTenantCreate'),
    path('untermieter/', views.SubTenantCreate.as_view(), name='SubTenantCreate'),
    path('anfragenliste/', views.Requests.as_view(), name='Requests'),
    path('impressum/', views.impressum, name='Impressum'),
    path('private/', include('private.urls'))
]