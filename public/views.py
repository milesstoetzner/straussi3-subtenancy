from django.shortcuts import render
from django.views import generic
from django.views.generic.list import ListView
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, SubTenantForm
import datetime


class MainTenantCreate(generic.CreateView):
    model = MainTenant
    form_class = MainTenantForm
    form_class.use_required_attribute = False

    # add success url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True
        return context


class SubTenantCreate(generic.CreateView):
    model = SubTenant
    form_class = SubTenantForm
    form_class.use_required_attribute = False

    # add success url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True
        return context


class Requests(generic.ListView):
    template_name = 'public/requests.html'

    def get_queryset(self):
        return SubTenant.objects.filter(active=True, end_subtenancy__gt=datetime.datetime.now()).order_by('begin_subtenancy','end_subtenancy')


def Index(request):
    return render(request, 'public/index.html')


def Impressum(request):
    return render(request, 'public/impressum.html')