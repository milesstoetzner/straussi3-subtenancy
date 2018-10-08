from django.shortcuts import render
from django.views import generic
from django.views.generic.list import ListView
from public.models import MainTenant, SubTenant
import datetime


class MainTenantCreate(generic.CreateView):
    model = MainTenant
    fields = '__all__'


class SubTenantCreate(generic.CreateView):
    model = SubTenant
    fields = '__all__'


class Requests(generic.ListView):
    template_name = 'public/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(active=True, end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


def Impressum(request):
    return render(request, 'public/impressum.html')