from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [

    # assistant
    path('contacts', views.Contacts.as_view(), name="Contacts"),
    path('search/', views.search, name='Search'),

    # contracts
    path('create', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('maintenant/<int:pk>', views.main_tenant_json, name='MainTenantJSON'),
    path('subtenant/<int:pk>', views.sub_tenant_json, name='SubTenantJSON'),
    path('view/<int:pk>/', views.ContractView.as_view(), name='ContractView'),
    path('update/<int:pk>/', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('pdf/<int:pk>/', views.ContractRender.as_view(), name='ContractRender'),

    # external
    path('active', views.ContractsActive.as_view(), name='ContractsActive'),
    path('archive', views.ContractsArchive.as_view(), name='ContractsArchive')

]
