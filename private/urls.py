from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    # for assistants
    path('subtenancy/', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('subtenancy/maintenant/<int:pk>', views.MainTenantJSON, name='MainTenantJSON'),
    path('subtenancy/subtenant/<int:pk>', views.SubTenantJSON, name='SubTenantJSON'),
    path('assistant/', views.Assistant.as_view(), name="Assistant"),
    path('maintenants/', views.MainTenantList.as_view(), name='MainTenantList'),
    path('maintenants/<int:pk>/', views.MainTenantUpdate.as_view(), name='MainTenantUpdate'),
    path('subtenants/', views.SubTenantList.as_view(), name='SubTenantList'),
    path('subtenants/<int:pk>/', views.SubTenantUpdate.as_view(), name='SubTenantUpdate'),
    path('contracts/', views.ContractList.as_view(), name='ContractList'),
    path('contracts/archive', views.ContractListArchive.as_view(), name='ContractListArchive'),
    path('contracts/<int:pk>/', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('contracts/<int:pk>/render/', views.ContractRender.as_view(), name='ContractRender'),

    # for external
    path('external', views.ContractsRunning.as_view(), name='ContractsRunning'),
    path('external/archive', views.ContractsRunningArchive.as_view(), name='ContractsRunningArchive')

]
