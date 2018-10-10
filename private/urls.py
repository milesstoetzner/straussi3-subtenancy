from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    path('ferienmiete/', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('assistent/', views.Assistant.as_view(), name="Assistant"),
    path('hauptmieter/', views.MainTenantList.as_view(), name='MainTenantList'),
    path('hauptmieter/<int:pk>/', views.MainTenantUpdate.as_view(), name='MainTenantUpdate'),
    path('untermieter/', views.SubTenantList.as_view(), name='SubTenantList'),
    path('untermieter/<int:pk>/', views.SubTenantUpdate.as_view(), name='SubTenantUpdate')


    # TODO: Verträge ansehen
    # TODO: Verträge ändern?
    # TODO: Aktive Ferienmiete
    # TODO: login

]