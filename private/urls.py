from django.urls import path
from . import views


urlpatterns = [

    path('ferienmiete/', views.ContractCreate.as_view(), name="Ferienmiete"),
    path('assistent/', views.Assistant, name="Assistant")
    # TODO: Hauptmieter ansehen
    # TODO: Hauptmieter ändern
    # TODO: Untermieter ansehen
    # TODO: Untermieter ändern
    # TODO: Verträge ansehen
    # TODO: Verträge ändern?
    # TODO: Aktive Ferienmiete
    # TODO: login

]