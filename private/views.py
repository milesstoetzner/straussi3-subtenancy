from django.views.generic import View, CreateView, ListView, UpdateView, DetailView
from .models import Contract
from public.models import MainTenant, SubTenant
from public.forms import MainTenantForm, MainTenantUpdateForm, SubTenantForm, SubTenantUpdateForm
from .forms import ContractForm, ContractUpdateForm
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.http import HttpResponse
from .utils import render_to_pdf


# TODO: authenticated and residential home scope for users, SWS and caretaker! (view, create, update, delete of contracts and main-/subtenants)


# TODO: display rent?!
# TODO: display donation?!
# TODO: display main_tenant details und sub_tenant details
class ContractCreate(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Contract
    form_class = ContractForm
    form_class.use_required_attribute = False

    # TODO: success url zur pdf
    # TODO: message ändern
    success_url = '/'
    success_message = 'Vertrag erfolgreich erstellt!'

    #TODO: scope!

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'private/contract_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get_queryset(self):
        return Contract.objects.filter(main_tenant__residential_home=self.request.user.administrative.residential_home).order_by('-id')


class ContractUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Contract
    form_class = ContractUpdateForm
    template_name = 'private/contract_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    # TODO: scope!

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# TODO: create contract templates
class ContractRender(LoginRequiredMixin, UserPassesTestMixin, View):
    # TODO: scope!

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get(self, request, *args, **kwargs):
        data = {
            'id': self.kwargs['pk']
        }
        pdf = render_to_pdf('private/contracts/contract_test.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class Assistant(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'private/assistent.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get_queryset(self):
        return SubTenant.objects.filter()


# OPTIMIZATION: not hardcoded view
class MainTenantList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'private/maintenant_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get_queryset(self):
        return MainTenant.objects.filter(residential_home=self.request.user.administrative.residential_home).order_by('-id')


class MainTenantUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MainTenant
    form_class = MainTenantUpdateForm
    template_name = 'private/maintenant_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    #TODO: scope

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


# OPTIMIZATION: not hardcoded view
class SubTenantList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'private/subtenant_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists()

    def get_queryset(self):
        return SubTenant.objects.all().order_by('-id')


class SubTenantUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SubTenant
    form_class = SubTenantUpdateForm
    template_name = 'private/subtenant_update_form.html'

    success_message = 'Änderungen erfolgreich übernommen!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['first'] = True  # TODO: better way to indicate first time resp. not validated form?
        return context


class ContractsRunning(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'private/contracts_running_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Assistants').exists() or self.request.user.groups.filter(name='External').exists()

    def get_queryset(self):
        return Contract.objects.filter(active='Ja', main_tenant__residential_home=self.request.user.administrative.residential_home)\
            .order_by('main_tenant__residential_home', 'main_tenant__house_number', 'main_tenant__room_number')