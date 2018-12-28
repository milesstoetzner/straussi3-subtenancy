from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [

    # assistant
    path('search/', views.search, name='Search'),

    # contracts
    path('create', views.create_contract , name="ContractCreate"),
    path('view/<int:pk>/', views.view_contract, name='ContractView'),
    path('update/<int:pk>/', views.update_contract, name='ContractUpdate'),
    # path('update/<int:pk>/', views.ContractUpdate.as_view(), name='ContractUpdate'),
    path('preview/<int:pk>/', views.preview_contract_pdf, name='ContractPreviewPDF'),
    path('save/<int:pk>/', views.save_contract_pdf, name='ContractSavePDF'),
    path('pdf/<int:pk>/<int:v>', views.view_contract_pdf, name='ContractViewPDF'),

    # external
    path('active', views.ContractsActive.as_view(), name='ContractsActive'),
    path('print', views.print_active_contracts, name='ContractsPrintActive'),
    path('archive', views.ContractsArchive.as_view(), name='ContractsArchive')

]
