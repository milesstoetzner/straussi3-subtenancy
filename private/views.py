from django.views.generic import View, CreateView, ListView, UpdateView, DetailView
from .models import Contract
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, MainTenantUpdateForm, SubTenantForm, SubTenantUpdateForm
from .forms import ContractForm, ContractUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.core import serializers
from django.http import HttpResponseRedirect

import json
import datetime

from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required

from django.http import HttpResponse
from .utils import render_to_pdf


# OPTIMIZE: nur ein create_form.html

# TODO: remove old submenants without contracts

# TODO: display main_tenant details und sub_tenant details
class ContractCreate(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Contract
    title = 'Vertrag erstellen'
    template_name = 'private/create_form.html'
    form_class = ContractForm
    form_class.use_required_attribute = False
    permission_required = 'private.add_contract'
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
        return reverse_lazy('private:ContractRender', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Aktive Verträge'
    template_name = 'private/contract_list.html'
    permission_required = 'private.view_contract'
    paginate_by = 50
    max_width = '100%'

    def get_queryset(self):
        return Contract.objects.filter(
            main_tenant__residential_home=self.request.user.administrative.residential_home).order_by('-id')


class ContractView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Contract
    context_object_name = 'object'
    form_class = ContractUpdateForm
    template_name = 'private/view.html'
    permission_required = 'private.view_contract'
    http_method_names = 'get'
    max_width = '600px'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get_success_url(self):
        return reverse_lazy('private:SubTenantView', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['type'] = 'contract'
        return context


class ContractUpdate(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Contract
    title = 'Vertrag ändern'
    form_class = ContractUpdateForm
    template_name = 'private/update_form.html'
    success_message = 'Änderungen erfolgreich übernommen!'
    permission_required = 'private.change_contract'
    max_width = '600px'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# TODO: create contract templates
class ContractRender(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    model = Contract
    permission_required = 'private.view_contract'

    def test_func(self):
        return self.get_object().main_tenant.residential_home == self.request.user.administrative.residential_home

    def get(self, request, *args, **kwargs):
        data = {
            'contract': self.get_object()
        }
        pdf = render_to_pdf('private/contracts/' + self.get_object().main_tenant.residential_home.short + '.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class Assistant(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Assistent'
    template_name = 'private/assistant.html'
    permission_required = 'public.view_subtenant'
    max_width = '800px'

    def get_queryset(self):
        return SubTenant.objects.filter()


# TODO: remove
# OPTIMIZE: not hardcoded view
class MainTenantList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Hauptmieter Übersicht'
    template_name = 'private/maintenant_list.html'
    permission_required = 'public.view_maintenant'
    paginate_by = 50
    max_width = '100%'

    def get_queryset(self):
        return MainTenant.objects.filter(residential_home=self.request.user.administrative.residential_home).order_by(
            '-id')


class MainTenantView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = MainTenant
    context_object_name = 'object'
    form_class = MainTenantUpdateForm
    template_name = 'private/view.html'
    permission_required = 'public.view_maintenant'
    http_method_names = 'get'
    max_width = '600px'

    def test_func(self):
        return self.get_object().residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['type'] = 'maintenant'
        return context


class MainTenantUpdate(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, SuccessMessageMixin,
                       UpdateView):
    model = MainTenant
    title = 'Hauptmieter ändern'
    form_class = MainTenantUpdateForm
    template_name = 'private/update_form.html'
    success_message = 'Änderungen erfolgreich übernommen!'
    permission_required = 'public.change_maintenant'
    max_width = '600px'

    def test_func(self):
        return self.get_object().residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# TODO: remove
# OPTIMIZE: not hardcoded view
class SubTenantList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Untermieter Übersicht'
    template_name = 'private/subtenant_list.html'
    permission_required = 'public.view_subtenant'
    paginate_by = 50
    max_width = '100%'

    def get_queryset(self):
        return SubTenant.objects.filter(
            Q(residential_home__isnull=True) | Q(residential_home=self.request.user.administrative.residential_home)).order_by(
            '-id')


class SubTenantView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SubTenant
    context_object_name = 'object'
    form_class = SubTenantUpdateForm
    template_name = 'private/view.html'
    permission_required = 'public.view_subtenant'
    http_method_names = 'get'
    max_width = '600px'

    def test_func(self):
        residential_home = self.get_object().residential_home
        return not residential_home or residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(self.get_object())
        context['type'] = 'subtenant'
        return context
    
    
class SubTenantUpdate(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, SuccessMessageMixin,
                      UpdateView):
    model = SubTenant
    title = 'Untermieter ändern'
    form_class = SubTenantUpdateForm
    template_name = 'private/update_form.html'
    success_message = 'Änderungen erfolgreich übernommen!'
    permission_required = 'public.change_subtenant'
    max_width = '600px'

    def test_func(self):
        residential_home = self.get_object().residential_home
        return not residential_home or residential_home == self.request.user.administrative.residential_home

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractExternalList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Aktive Ferienmiete'
    template_name = 'private/contract_external_list.html'
    permission_required = 'private.view_contract'
    paginate_by = 50
    max_width = '100%'

    def get_queryset(self):
        return Contract.objects.filter(active='Ja',
                                       main_tenant__residential_home=self.request.user.administrative.residential_home, end__gte=datetime.datetime.now()) \
            .order_by('main_tenant__residential_home', 'main_tenant__house_number', 'main_tenant__room_number')


class ContractExternalArchive(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    title = 'Ferienmiete Archiv'
    template_name = 'private/contract_external_list.html'
    permission_required = 'private.view_contract'
    paginate_by = 50
    max_width = '100%'

    def get_queryset(self):
        return Contract.objects.filter(active='Ja',
                                       main_tenant__residential_home=self.request.user.administrative.residential_home,
                                       end__lt=datetime.datetime.now()) \
            .order_by('main_tenant__residential_home', 'main_tenant__house_number', 'main_tenant__room_number')


@login_required
@permission_required('public.view_maintenant')
def MainTenantJSON(request, pk):
    obj = MainTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')


@login_required
@permission_required('public.view_subtenant')
def SubTenantJSON(request, pk):
    obj = SubTenant.objects.get(pk=pk)
    data = serializers.serialize('json', [obj, ])
    struct = json.loads(data)
    data = json.dumps(struct[0])

    return HttpResponse(data, content_type='application/json')
