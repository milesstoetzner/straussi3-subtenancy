from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [

    # assistant
    path('search/', views.search, name='Search'),

    # contracts
    path('create', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('view/<int:pk>/', views.ContractView.as_view(), name='ContractView'),
    path('update/<int:pk>/', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('preview/<int:pk>/', views.ContractPreviewPDF.as_view(), name='ContractPreviewPDF'),
    path('render/<int:pk>/', views.ContractRenderPDF.as_view(), name='ContractRenderPDF'),
    path('pdf/<int:pk>/', views.ContractViewPDF.as_view(), name='ContractViewPDF'),

    path('maintenant/<int:pk>', views.main_tenant_json, name='MainTenantJSON'),
    path('subtenant/<int:pk>', views.sub_tenant_json, name='SubTenantJSON'),

    # external
    path('active', views.ContractsActive.as_view(), name='ContractsActive'),
    path('archive', views.ContractsArchive.as_view(), name='ContractsArchive')

]
