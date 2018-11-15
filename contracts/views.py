from django.views.generic import View, CreateView, ListView, UpdateView, DetailView
from .models import Contract
from tenants.models import MainTenant, SubTenant
from tenants.forms import MainTenantForm, MainTenantUpdateForm, SubTenantForm, SubTenantUpdateForm
from .forms import ContractForm, ContractUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core import serializers
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render

import json
import datetime

from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse
from .utils import render_to_pdf

# TODO: remove residential home scope!

# TODO: remove old subtenants without contracts


# TODO: display main_tenant details und sub_tenant details
class ContractCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Contract
    title = 'Vertrag erstellen'
    template_name = 'contracts/create.html'
    form_class = ContractForm
    form_class.use_required_attribute = False
    permission_required = 'contracts.add_contract'
    max_width = '600px'

    # TODO: scope of main and sub!

    # TODO: save contracts as pdf?

    def form_valid(self, form):
        self.object = form.save()  # TODO: was bedeutet 'Instance attribute object defined outside __init__'?!
        self.object.main_tenant.active = 'Nein' # TODO: removet this?!
        self.object.main_tenant.save()
        self.object.sub_tenant.active = 'Nein'
        self.object.sub_tenant.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('contracts:ContractRender', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Contract
    context_object_name = 'object'
    form_class = ContractUpdateForm
    template_name = 'contracts/view.html'
    permission_required = 'contracts.view_contract'
    http_method_names = 'get'
    max_width = '600px'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get_success_url(self):
        return reverse_lazy('contracts:SubTenantView', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['type'] = 'contract'
        return context


class ContractUpdate(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Contract
    title = 'Vertrag ändern'
    form_class = ContractUpdateForm
    template_name = 'contracts/update.html'
    success_message = 'Änderungen erfolgreich übernommen!'
    permission_required = 'contracts.change_contract'
    max_width = '600px'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['get'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# TODO: create contract templates
class ContractRender(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    model = Contract
    permission_required = 'contracts.view_contract'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get(self, request, *args, **kwargs):
        data = {
            'contract': self.get_object()
        }
        pdf = render_to_pdf('contracts/contracts/' + self.get_object().main_tenant.residential_home.short + '.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class ContractsActive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Aktive Verträge'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'

    def test_func(self):
        return self.request.user.is_assistant or self.request.user.is_external or self.request.user.is_staff

    def get_queryset(self):
        return Contract.objects.filter(is_active=True, end__gte=datetime.datetime.now()) \
            .order_by('main_tenant__residential_home', 'main_tenant__house_number', 'main_tenant__room_number')


class ContractsArchive(LoginRequiredMixin, UserPassesTestMixin, ListView):
    title = 'Archiv'
    template_name = 'contracts/list.html'
    paginate_by = 50
    max_width = '100%'

    def test_func(self):
        return self.request.user.is_assistant or self.request.user.is_external or self.request.user.is_staff

    def get_queryset(self):
        return Contract.objects.filter(is_active=True, end__lt=datetime.datetime.now()) \
            .order_by('main_tenant__residential_home', 'main_tenant__house_number', 'main_tenant__room_number')


@csrf_protect
@login_required
@permission_required(['tenants.view_maintenant', 'tenants.view_subtenant', 'contracts.view_contract'])
@require_POST
def search(request):
    query = request.POST['query']

    # TODO: complex query! full name, birthday, tenant_id
    main_tenants = MainTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    sub_tenants = SubTenant.objects.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))

    context = {
        'main_tenants': main_tenants,
        'sub_tenants': sub_tenants,
        'query': query
    }

    return render(request, 'contracts/search_result.html', context)


@login_required
@permission_required('tenants.view_maintenant')
def main_tenant_json(request, pk):
    obj = MainTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')


@login_required
@permission_required('tenants.view_subtenant')
def sub_tenant_json(request, pk):
    obj = SubTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')
