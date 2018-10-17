from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    # for assistants
    path('ferienmiete/', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('ferienmiete/maintenant/<int:pk>', views.MainTenantJSON, name='MainTenantJSON'),
    path('ferienmiete/subtenant/<int:pk>', views.SubTenantJSON, name='SubTenantJSON'),
    path('assistent/', views.Assistant.as_view(), name="Assistant"),
    path('hauptmieter/', views.MainTenantList.as_view(), name='MainTenantList'),
    path('hauptmieter/<int:pk>/', views.MainTenantUpdate.as_view(), name='MainTenantUpdate'),
    path('untermieter/', views.SubTenantList.as_view(), name='SubTenantList'),
    path('untermieter/<int:pk>/', views.SubTenantUpdate.as_view(), name='SubTenantUpdate'),
    path('vertraege/', views.ContractList.as_view(), name='ContractList'),
    path('vertraege/archive', views.ContractListArchive.as_view(), name='ContractListArchive'),
    path('vertraege/<int:pk>/', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('vertraege/<int:pk>/render/', views.ContractRender.as_view(), name='ContractRender'),

    # for external
    path('external', views.ContractsRunning.as_view(), name='ContractsRunning'),
    path('external/archive', views.ContractsRunningArchive.as_view(), name='ContractsRunningArchive')

]
