from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    path('ferienmiete/', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('assistent/', views.Assistant, name="Assistant"),
    path('hauptmieter/', views.MainTenantList.as_view(), name='MainTenantList'),
    path('hauptmieter/<int:pk>/', views.MainTenantUpdate.as_view(), name='MainTenantUpdate')

    # TODO: Hauptmieter ändern
    # TODO: Untermieter ansehen
    # TODO: Untermieter ändern
    # TODO: Verträge ansehen
    # TODO: Verträge ändern?
    # TODO: Aktive Ferienmiete
    # TODO: login

]