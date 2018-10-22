from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    # assistant
    path('assistant/', views.Assistant.as_view(), name="Assistant"),

    # maintenants
    path('maintenants/', views.MainTenantList.as_view(), name='MainTenantList'),
    path('maintenants/<int:pk>/view', views.MainTenantView.as_view(), name='MainTenantView'),
    path('maintenants/<int:pk>/update', views.MainTenantUpdate.as_view(), name='MainTenantUpdate'),

    # subtenants
    path('subtenants/', views.SubTenantList.as_view(), name='SubTenantList'),
    path('subtenants/<int:pk>/view', views.SubTenantView.as_view(), name='SubTenantView'),
    path('subtenants/<int:pk>/update', views.SubTenantUpdate.as_view(), name='SubTenantUpdate'),

    # contracts
    path('contracts/', views.ContractList.as_view(), name='ContractList'),
    path('contracts/create', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('contracts/maintenant/<int:pk>', views.MainTenantJSON, name='MainTenantJSON'),
    path('contracts/subtenant/<int:pk>', views.SubTenantJSON, name='SubTenantJSON'),
    path('contracts/<int:pk>/view', views.ContractView.as_view(), name='ContractView'),
    path('contracts/<int:pk>/update', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('contracts/<int:pk>/render/', views.ContractRender.as_view(), name='ContractRender'),

    # external
    path('external', views.ContractExternalList.as_view(), name='ContractExternalList'),
    path('external/archive', views.ContractExternalArchive.as_view(), name='ContractExternalArchive')

]
