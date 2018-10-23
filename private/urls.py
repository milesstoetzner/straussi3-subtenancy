from django.urls import path
from . import views

app_name = 'private'

urlpatterns = [

    # assistant
    path('assistant/', views.Assistant.as_view(), name="Assistant"),
    path('search/', views.search, name='Search'),

    # maintenants
    path('maintenants/<int:pk>/view', views.MainTenantView.as_view(), name='MainTenantView'),
    path('maintenants/<int:pk>/update', views.MainTenantUpdate.as_view(), name='MainTenantUpdate'),

    # subtenants
    path('subtenants/<int:pk>/view', views.SubTenantView.as_view(), name='SubTenantView'),
    path('subtenants/<int:pk>/update', views.SubTenantUpdate.as_view(), name='SubTenantUpdate'),

    # contracts
    path('contracts/create', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('contracts/maintenant/<int:pk>', views.main_tenant_json, name='MainTenantJSON'),
    path('contracts/subtenant/<int:pk>', views.sub_tenant_json, name='SubTenantJSON'),
    path('contracts/<int:pk>/view', views.ContractView.as_view(), name='ContractView'),
    path('contracts/<int:pk>/update', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('contracts/<int:pk>/render/', views.ContractRender.as_view(), name='ContractRender'),

    # external
    path('external', views.ContractExternalList.as_view(), name='ContractExternalList'),
    path('external/archive', views.ContractExternalArchive.as_view(), name='ContractExternalArchive')

]
